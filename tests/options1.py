import nextmv

options = nextmv.Options(
    nextmv.Parameter("duration", str, "30s", description="solver duration", required=True),
    nextmv.Parameter("threads", int, 4, description="computer threads", required=True),
)

print(options.to_dict())
