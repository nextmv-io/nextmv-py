import nextmv

options = nextmv.Options(
    nextmv.Parameter("foo", str, choices=["bar", "baz"]),
    nextmv.Parameter("prime", int, choices=[11, 13, 17], required=True),
    nextmv.Parameter("xyzzy", str, choices=["xyzzy", "plugh"], default="xyzzy"),
)

print(options.to_dict())
