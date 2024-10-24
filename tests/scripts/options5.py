import nextmv

options = nextmv.Options(
    nextmv.Parameter("str_opt", str, default=None),
)

print(f"str_opt: {options.str_opt}")
