from pyshell.execution.redirection import output_to_target
from pyshell.registry import registry


@registry.register("jobs")
def run(args, ctx):
    for line in ctx.jobs.render():
        output_to_target(line)
    return 0
