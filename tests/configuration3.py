import nextmv

config = nextmv.Configuration(
    nextmv.Parameter("duration", str),
    nextmv.Parameter("threads", int),
)

print(config.to_dict())
