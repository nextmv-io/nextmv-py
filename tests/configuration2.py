import nextmv

config = nextmv.Configuration(
    nextmv.Parameter("duration", str, description="solver duration", required=True),
    nextmv.Parameter("threads", int, description="computer threads", required=True),
)

print(config.to_dict())
