This is a formal grammar for the language parsed by pycson.
It uses the standard [PEG syntax][1] with an extension
to support indent sensitivity: for a PEG expression `E`,
the expression `E{I=e}` will change the meaning of the identifier `I`
to the expression `e` while matching `E`.

In CSON, whitespace may contain spaces and tabs. This is more strict than
Coffeescript where any `[^\n\S]` will match.
The symbol `nl` will match one or more newlines that only contain whitespace
or comments in between. A match for `nl` also matches any whitespace preceding the first
newline. `ews` is the "extended whitespace", one that incudes newlines.
Note however that `ews` ending in a comment must be terminated by a newline character.

    ws <- [ \t]*
    nl <- (ws ('#' [^\n]*)? '\r'? '\n')+
    ews <- nl? ws

Atomic values of type `null` and `bool`.

    null <- 'null'
    bool <- 'false' / 'true'

Number can be decimal, binary, hexadecimal or octal. Decimal numbers
must not have any leading zeros. The octal prefix is `0o`, and therefore
numbers like `0775` are not allowed (use `0o755` instead).
Hex digits are case-insensitive, but the `0x` prefix (and `0o` and `0b`)
must be lowercase. There is no way to make a non-decimal number negative.

    number <- '0b'[01]+ / '0o'[0-7]+ / 0x[0-9a-fA-F]+
        / -?([1-9][0-9]* / '0')?'.'[0-9]+('e'[+-]?[0-9]+)?
        / -?([1-9][0-9]* / '0')('.'[0-9]+)?('e'[+-]?[0-9]+)?

Strings are delimited by one of `'`, `"`, `'''` or `"""`. There is no
difference between apostrophes and double quotes, since string interpolation
is treated literally. This means that `"#{var}"` is the same as `"\#{var}"`.
Even more importantly, `"#{"test"}"` is not a valid CSON string.

All escapes are treated literally, except for `r`, `n`, `t`, `f`, and `b`, which are
treated as is usually in all modern languages, and for a newline character.
Escaping a newline character is equivalent to removing the newline and any following
whitespace.

Single-quoted strings treat newlines and any following whitespace as a single space.
Lines containing only whitespace are ignored. Leading and trailing whitespace is ignored.

For block strings (triple-quoted strings) that contain a newline, the first line is stripped
if it only contains whitespace. Similarly for the last line. Escaped newline is treated the
same way as for single-quoted strings (removes the newline and any following whitespace).
Once assembled, a maximal prefix of whitespace characters that occurs at the beginning
of each line is found and stripped from all lines.

    string <-
        "'" !"''" string_tail{X="'"} /
        "'''" string_tail{X="'''"} /
        '"' !'""' string_tail{X='""'} /
        '"""' string_tail{X='"""'}
    string_tail <- (!X ('\\'. / .))* X

Identifiers may be used instead of strings as keys in objects.

    id <- [$a-zA-Z_][$0-9a-zA-Z_]*

Arrays are delimited by brackets. Whitespace is insignificant and the current indent level is reset.

    array <-
        '[' (array_value (ews ',' array_value / nl (object / ews simple_value))* (ews ',')?)?{I=} ews ']'
    array_value <- nl object / ws line_object / ews simple_value

This rule matches a brace-delimited object. The handling of whitespace is the same
as for arrays, the indent is reset.

    flow_kv <- (id / string) ews ':'
        (nl object / ws line_object / ews simple_value)
    flow_obj_sep <- ews ',' ews / nl ws
    flow_object <- '{' ews (flow_kv  (flow_obj_sep flow_kv)* ews (',' ews)?)?{I=} '}'

A simple value is one which is not sensitive to the position within the document
or to the current indent level.

    simple_value <- null / bool / number / string / array / flow_object

A line object is an unbraced object which doesn't start at its own line.
For example, in `[a:1, b:2]`, the array contains one `line_object`.
Note that a line object will never span multiple lines.
Line objects have no indent, but they propagate the current indent level to their
child objects.

    line_kv <- (id / string) ws ':' ws
        (nl I indented_object / line_object / simple_value / nl I [ \t] ws simple_value)
    line_object <- line_kv (ws ',' ws line_kv)*?

This is the unbraced object that starts on its own line. It detects its ident level
and requires that all lines have this indent. The previous indent level must be
a string prefix of the newly detected one.

    object <- ' ' object{I=I ' '} / '\t' object{I=I '\t'} / line_object (ws ','? nl I line_object)*
    indented_object <- ' ' object{I=I ' '} / '\t' object{I=I '\t'}

A CSON document consists of a single value (either an unbraced `object` or a `simple_value`).
The value can be preceded and followed by whitespace. Note that a comment
on the last line must be terminated by a newline.

    root=nl? (object{I=} ws ','? / ws simple_value) ews !.

  [1]: http://www.brynosaurus.com/pub/lang/peg.pdf
