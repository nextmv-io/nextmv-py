import nextmv

options = nextmv.Options(
    nextmv.Option("duration", str),
    nextmv.Option("threads", int),
)

print(options.to_dict())
