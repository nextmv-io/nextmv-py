import nextmv

config = nextmv.Configuration(
    nextmv.Parameter("duration", str, "30s", description="solver duration", required=True),
    nextmv.Parameter("threads", int, 4, description="computer threads", required=True),
)

print(config.to_dict())
