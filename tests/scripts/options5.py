import nextmv

options = nextmv.Options(
    nextmv.Parameter("str_opt", str, default=None),
)

print(options.to_dict())
