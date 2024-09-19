import nextmv

options = nextmv.Options(
    nextmv.Parameter("duration", str, "30s", description="solver duration"),
    nextmv.Parameter("threads", int, 4, description="computer threads"),
)

print(options.to_dict())
