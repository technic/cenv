"""Console script for cenv_script."""
import sys
from functools import wraps
import traceback
import click
from cenv_script.cenv_script import CondaEnv, CondaEnvException


def catch(func):
    @wraps(func)
    def wrapper(ctx, *args, **kwargs):
        try:
            func(ctx, *args, **kwargs)
        except CondaEnvException as ex:
            if ctx.obj['verbose']:
                print("\n")
                traceback.print_exc()
                print("\n")
            print("error:", ex)
            return 1
        return 0

    return wrapper


@click.group()
@click.option("--verbose", is_flag=True, help="print exceptions traceback")
@click.pass_context
def main(ctx, verbose=False):
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose


@main.command()
@click.pass_context
@click.argument("package")
@catch
def install(ctx, package):
    """Install conda package"""
    e = CondaEnv()
    e.install(package)


@main.command()
@click.pass_context
@click.argument("package")
@catch
def remove(ctx, package):
    """Remove conda package"""
    e = CondaEnv()
    e.remove(package)


@main.command()
@click.pass_context
@click.argument("package")
@catch
def pip_install(ctx, package):
    """Install package with pip"""
    e = CondaEnv()
    e.pip_install(package)


@main.command()
@click.pass_context
@click.argument("package")
@catch
def pip_remove(ctx, package):
    """Remove package with pip"""
    e = CondaEnv()
    e.pip_remove(package)


if __name__ == "__main__":
    sys.exit(main(obj={}))  # pylint: disable-all # pragma: no cover
