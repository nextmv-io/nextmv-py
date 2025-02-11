import nextmv

options = nextmv.Options(
    nextmv.Parameter("bool_opt", bool, default=True),
)

print(options.to_dict())
