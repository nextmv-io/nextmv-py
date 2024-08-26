import nextmv

options = nextmv.Options(
    nextmv.Parameter("duration", str),
    nextmv.Parameter("threads", int),
)

print(options.to_dict())
