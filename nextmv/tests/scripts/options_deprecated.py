import nextmv

options = nextmv.Options(
    nextmv.Option("duration", str, description="solver duration", required=True),
    nextmv.Parameter("threads", int, description="computer threads", required=True),
)

print(options.to_dict())
