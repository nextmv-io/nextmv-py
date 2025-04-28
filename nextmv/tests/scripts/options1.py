import nextmv

options = nextmv.Options(
    nextmv.Option("duration", str, "30s", description="solver duration"),
    nextmv.Option("threads", int, 4, description="computer threads"),
)

print(options.to_dict())
