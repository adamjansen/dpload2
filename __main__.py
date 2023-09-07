import errno
import sys
import time
import logging
import struct
import io

import can
import rich
import click
import intelhex

import rich.progress
import rich.traceback
from rich.console import Console
from rich.table import Table
from rich.logging import RichHandler

from .dpload import DPLoad
from .protocol import crc16

VERSION = "2.0"

console = Console()
error_console = Console(stderr=True)

PAGE_SIZE = 4096


class BasedIntParamType(click.ParamType):
    name = "integer"

    def convert(self, value, param, ctx):
        if isinstance(value, int):
            return value

        try:
            return int(value, 0)
        except ValueError:
            self.fail(f"{value!r} is not a valid integer", param, ctx)
        return value


BASED_INT = BasedIntParamType()


class RangedBasedIntParamType(BasedIntParamType):
    name = "integer"

    def __init__(self, min=None, max=None, *args, **kwargs):
        self.min = min
        self.max = max
        BasedIntParamType.__init__(self, *args, **kwargs)

    def convert(self, value, param, ctx):
        v = BasedIntParamType.convert(self, value, param, ctx)
        if self.min is not None and v < self.min:
            raise ValueError(f"Value {v} is below minimum {self.min}")
        if self.max is not None and v > self.max:
            raise ValueError(f"Value {v} is above maximum {self.max}")
        return v


class MultiRangeBasedIntParamType(BasedIntParamType):
    def __init__(self, ranges, *args, **kwargs):
        self.ranges = ranges
        BasedIntParamType.__init__(self, *args, **kwargs)

    def convert(self, value, param, ctx):
        v = BasedIntParamType.convert(self, value, param, ctx)
        valid = any((v >= min and v <= max) for min, max in self.ranges)
        if not valid:
            range_text = ", ".join(f"{min}-{max}" for (min, max) in self.ranges)
            raise ValueError(f"Value {v} is not in any of the ranges {range_text}")
        return v


SA_TYPE = RangedBasedIntParamType(min=0, max=253)
SA_TYPE.name = "NODE"

SA_OR_GLOBAL_TYPE = MultiRangeBasedIntParamType([(0, 253), (255, 255)])
SA_OR_GLOBAL_TYPE.name = "NODE-OR-GLOBAL"

APP_ADDRESS_TYPE = RangedBasedIntParamType(min=0xC000, max=0xC000 + 0x32000)


@click.group()
@click.option(
    "--bus", default="can0", help="SocketCAN network interface", show_default=True
)
@click.option("--verbose", default=False, is_flag=True, help="Output extra information")
@click.option(
    "--bitrate",
    default=250000,
    help="CAN bitrate, in bits per second",
    show_default=True,
)
@click.option(
    "--sa",
    default=39,
    help="J1939 source address for transmitted messages",
    show_default=True,
    type=SA_TYPE,
)
@click.pass_context
def cli(ctx, bus, verbose, bitrate, sa):
    logging.getLogger("can.interfaces").setLevel(logging.WARN)
    log_level = logging.DEBUG if verbose else logging.WARN
    logging.basicConfig(level=log_level, handlers=[RichHandler()])
    rich.traceback.install(show_locals=True)
    ctx.obj = DPLoad(bus=bus, bitrate=bitrate, sa=sa)


@cli.command()
@click.argument("hexfile", type=click.Path(exists=True))
@click.option("--da", default=None, help="Address of node to program", type=SA_TYPE)
@click.pass_obj
def verify(dpload, hexfile, da):
    """Verify programming"""
    ih = intelhex.IntelHex()
    ih.fromfile(hexfile, format="hex")

    segments = ih.segments()
    for start, stop in segments:
        size = stop - start + 1
        console.print(
            f"Verify [bold white]0x{start:08x}...0x{stop:08x}[/bold white] [dim white]{size:8d} bytes[/dim white] ",
            end="",
        )
        if not (0x1D007000 <= start < 0x1D080000):
            console.print("[bold blue]⏭ SKIP[/bold blue]")
            continue
        data = ih.tobinstr(start, stop)
        reference_crc = crc16(data)
        try:
            target_crc = dpload.get_crc(da=da, timeout=5, start=start, size=size)
        except TimeoutError:
            console.print("[bold red]:cross_mark:ERROR:[/bold red] Could not get CRC")
        else:
            if reference_crc != target_crc:
                console.print(
                    f"[bold red]:cross_mark:ERROR:[/bold red] Bad CRC. Expected {reference_crc:04X}, but got {target_crc:04X}"
                )
            else:
                console.print(
                    f"[bold green]:white_heavy_check_mark:OK[/bold green] {reference_crc:04X}"
                )


@cli.command()
@click.argument("hexfile", type=click.Path(exists=True))
@click.option("--da", default=None, help="Address of node to program", type=SA_TYPE)
@click.option(
    "--stay",
    default=False,
    is_flag=True,
    help="Do not jump to application; stay in bootloader",
)
@click.option(
    "--unsafe",
    default=False,
    is_flag=True,
    help="Ignore part number information in the hexfile [DANGEROUS]",
)
@click.confirmation_option(
    prompt="Are you sure you want to erase and re-program the node?"
)
@click.pass_obj
def program(dpload, hexfile, da, stay, unsafe):
    """Load a hexfile onto the controller"""
    records = []
    with rich.progress.open(hexfile, "r", description="Reading hex file") as f:
        for line in f.readlines():
            try:
                record = bytes.fromhex(line[1:].strip())
            except ValueError:
                raise ValueError(f"Bad record format: {line}")
            records.append(record)

    # dpload.boot_can(da=da)
    time.sleep(0.500)

    try:
        base, pn, appmajor, appminor = dpload.get_oem_info(da=da)
    except TimeoutError:
        error_console.print(
            f"[bold red]:cross_mark: ERROR:[/bold red] Timeout waiting for OEM info"
        )
        sys.exit(1)
    except can.exceptions.CanOperationError as e:
        if e.error_code == errno.ENETDOWN:
            error_console.print(
                f"[bold red]:cross_mark: ERROR:[/bold red] CAN interface {dpload.busname} is down"
            )
        else:
            error_console.print(f"CAN error {e.error_code}: {e}")
        sys.exit(1)

    console.print("Erasing flash")
    try:
        dpload.erase(da=da, timeout=5.0)
    except TimeoutError:
        error_console.print(
            f"[bold red]:cross_mark:[/bold red] Timeout waiting for response"
        )
        sys.exit(1)

    start = time.time()
    chunk = b""
    n = 0
    dpload.dm13_control(True)
    for record in rich.progress.track(records, description="Writing flash..."):
        n += 1
        chunk += record
        if n == 8:
            dpload.program_flash(chunk, da=da, timeout=5.0)
            time.sleep(0.005)
            chunk = b""
            n = 0
    if n:
        dpload.program_flash(chunk, da=da, timeout=5.0)

    dpload.dm13_control(False)
    elapsed = time.time() - start
    console.print(f"Programming completed in {elapsed:0.3f} seconds")

    if not stay:
        console.print("[bold blue]:play_button:[/bold blue] Starting application")
        try:
            dpload.jump(da=da)
        except TimeoutError:
            pass
    else:
        console.print("[bold blue]:pause_button:[/bold blue] Staying in bootloader")


@cli.command()
@click.option(
    "--da", default=208, help="Node to start", show_default=True, type=SA_TYPE
)
@click.pass_obj
def jump(dpload, da):
    """Exit the bootloader and start the application"""
    try:
        dpload.jump(da=da)
        console.print(
            f"[bold green] :white_heavy_check_mark:[/bold green] Node {da} ({da:#02x}) started application"
        )
    except TimeoutError:
        error_console.print(
            f"[bold red]:cross_mark:[/bold red] Application did not start"
        )
        sys.exit(1)


@cli.command()
@click.option(
    "--da",
    default=208,
    show_default=True,
    help="Node to retrieve info for",
    type=SA_TYPE,
)
@click.pass_obj
def info(dpload, da):
    """Retrieve information about a node"""
    try:
        base, pn, pnmajor, pnminor = dpload.get_oem_info(da=da)
        appmajor, appminor = dpload.get_app_info(da=da, timeout=0.5)
    except TimeoutError:
        error_console.print("[bold red]:cross_mark:[/bold red] Node did not respond")
        sys.exit(1)
    else:
        console.print(f"P/N {pn} {pnmajor:x}.{pnminor:x}")
        if (appmajor, appminor) == (0xFF, 0xFF):
            console.print("No application loaded")
        else:
            console.print(f"App {appmajor:x}.{appminor:x}")


@cli.command()
@click.option(
    "--da",
    default=None,
    help="Node to start",
    show_default=True,
    type=SA_OR_GLOBAL_TYPE,
)
@click.option(
    "--usb", default=False, is_flag=True, help="Use USB update mode instead of CAN"
)
@click.pass_obj
def boot(dpload, da, usb):
    """
    Enter the bootloader

    NOTE: The application must be running correclty.
    """
    return
    if usb:
        dpload.boot_usb(da=da)
        console.print(f"Sent request to enter USB bootloader")
    else:
        dpload.boot_can(da=da)
        console.print(f"Sent request to enter CAN bootloader")


@cli.command()
@click.option(
    "--da", default=None, help="Node to start", show_default=True, type=SA_TYPE
)
@click.option(
    "--start",
    default=0x1D007000,
    help="Start address of data to checksum",
    show_default=True,
    type=APP_ADDRESS_TYPE,
)
@click.option(
    "--size",
    default=0x79000,
    help="Size of data in bytes",
    show_default=True,
    type=BASED_INT,
)
@click.option(
    "--pagewise",
    default=False,
    is_flag=True,
    help="Show CRC of each page, as well as the overall CRC",
)
@click.pass_obj
def crc(dpload, da, start, size, pagewise):
    """
    Request application CRC
    """
    if not pagewise:
        try:
            crc = dpload.get_crc(da=da, timeout=5, start=start, size=size)
        except TimeoutError:
            error_console.print(f"[bold red]:cross_mark:[/bold red] Could not get CRC")
            sys.exit(1)
    else:
        page_crcs = []
        BLANK_PAGE = b"\x00" * PAGE_SIZE
        try:
            for address in rich.progress.track(
                range(start, start + size, PAGE_SIZE),
                description="Calculating CRC",
                console=console,
            ):
                page_crc = dpload.get_crc(
                    da=da, timeout=3, start=address, size=PAGE_SIZE
                )
                console.print(f"Page {address:#08x}: {page_crc:04X}")
                page_crcs.append(page_crc)
        except TimeoutError:
            error_console.print(f"[bold red]:cross_mark:[/bold red] Could not get CRC")
            sys.exit(1)
        crc = 0x0000
        for page, page_crc in enumerate(page_crcs):
            crc = crc16(BLANK_PAGE, start=crc)
            crc ^= page_crc
            address = 0x1D007000 + page * PAGE_SIZE

    console.print(f"CRC-16 (CCITT): {crc:04X}")


@cli.command()
@click.option(
    "--start", default=0, help="First node to scan", show_default=True, type=SA_TYPE
)
@click.option(
    "--end", default=253, help="Last node to scan", show_default=True, type=SA_TYPE
)
@click.pass_obj
def scan(dpload, start, end):
    """Scan CAN bus for nodes"""
    nodes = []
    for da in rich.progress.track(
        range(start, end + 1),
        description="Scanning CAN bus",
        console=console,
        auto_refresh=False,
    ):
        if da == dpload.sa:
            continue
        try:
            major, minor = dpload.get_boot_info(da=da, timeout=0.1)
        except TimeoutError:
            continue
        except ValueError:
            continue
        except can.exceptions.CanOperationError:
            error_console.print("\n[bold red]ERROR:[/bold red] Cannot complete scan")
            break
        nodes.append((da, major, minor))

    table = Table(title="Active nodes")
    table.add_column("Node Address", justify="right", style="cyan")
    table.add_column("P/N", justify="center", style="blue")
    table.add_column("Bootloader", justify="center", style="green")
    table.add_column("Application", justify="right", style="green")

    for da, major, minor in nodes:
        base, pn, pnmajor, pnminor = dpload.get_oem_info(da=da, timeout=0.5)
        try:
            appmajor, appminor = dpload.get_app_info(da=da, timeout=0.5)
        except TimeoutError:
            app_info = "?"
        else:
            app_info = f"{appmajor:x}.{appminor:x}"

        table.add_row(
            f"{da} ({da:#02x})",
            f"{pn} {pnmajor:x}.{pnminor:x}",
            f"{major:x}.{minor:x}",
            app_info,
        )
    console.print(table)


if __name__ == "__main__":
    cli()
