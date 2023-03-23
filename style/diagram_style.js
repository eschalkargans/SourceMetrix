function DiagramStyle(
    criteria,
    criteriaLabel,
    backgroundColor,
    borderColor,
    index
) {
    this.criteria = criteria;
    this.criteriaLabel = criteriaLabel;
    this.backgroundColor = backgroundColor;
    this.borderColor = borderColor;
    this.index = index;
}

const DiagramStyles = new Map();

CRITERIA_LABELS = {
    "std.code.complexity.cyclomatic": "std.code.complexity.cyclomatic",
    "std.code.complexity.maxindent": "std.code.complexity.maxindent",
    "std.code.filelines.code": "std.code.filelines.code",
    "std.code.filelines.preprocessor": "std.code.filelines.preprocessor",
    "std.code.filelines.comments": "std.code.filelines.comments",
    "std.code.filelines.total": "std.code.filelines.total",
    "std.code.length.total": "std.code.length.total",
    "std.code.lines.code": "std.code.lines.code",
    "std.code.lines.preprocessor": "std.code.lines.preprocessor",
    "std.code.lines.comments": "std.code.lines.comments",
    "std.code.lines.total": "std.code.lines.total",
    "std.code.longlines": "std.code.longlines",
    "std.code.longlines.limit=120": "std.code.longlines.limit=120",
    "std.code.magic.numbers": "std.code.magic.numbers",
    "std.code.magic.numbers.simplier": "std.code.magic.numbers.simplier",
    "std.code.member.fields": "std.code.member.fields",
    "std.code.member.globals": "std.code.member.globals",
    "std.code.member.classes": "std.code.member.classes",
    "std.code.member.structs": "std.code.member.structs",
    "std.code.member.interfaces": "std.code.member.interfaces",
    "std.code.member.types": "std.code.member.types",
    "std.code.member.methods": "std.code.member.methods",
    "std.code.member.namespaces": "std.code.member.namespaces",
    "std.code.maintindex.simple": "std.code.maintindex.simple",
    "std.code.ratio.comments": "std.code.ratio.comments",
    "std.code.todo.comments": "std.code.todo.comments",
    "std.code.todo.strings": "std.code.todo.strings",
    "std.suppress": "std.suppress",
    "std.general.procerrors": "std.general.procerrors",
    "std.general.size": "std.general.size",
};

for (const key in CRITERIA_LABELS) {
    DiagramStyles.set(
        key,
        new DiagramStyle(key, CRITERIA_LABELS[key], "orange", "red", 6)
    );
}

// DiagramStyles.set(
//     "std.code.complexity.cyclomatic",
//     new DiagramStyle(
//         "std.code.complexity.cyclomatic",
//         "cyclomatic complexity",
//         "orange",
//         "red",
//         6
//     )
// );

// DiagramStyles.set(
//     "std.code.lines.code",
//     new DiagramStyle(
//         "std.code.lines.code",
//         "lines of code per file",
//         "lightblue",
//         "blue",
//         8
//     )
// );

// DiagramStyles.set(
//     "std.code.filelines.comments",
//     new DiagramStyle(
//         "std.code.filelines.comments",
//         "lines of comment per file",
//         "lightgreen",
//         "green",
//         7
//     )
// );
