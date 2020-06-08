function DiagramStyle(criteria, criteriaLabel, backgroundColor, borderColor, index)
{
    this.criteria = criteria;
    this.criteriaLabel = criteriaLabel;
    this.backgroundColor = backgroundColor;
    this.borderColor = borderColor;
    this.index = index;
}

const DiagramStyles = new Map;

DiagramStyles.set('std.code.complexity.cyclomatic',
    new DiagramStyle('std.code.complexity.cyclomatic', 'cyclomatic complexity', 'orange', 'red', 6)
);

DiagramStyles.set('std.code.lines.code',
    new DiagramStyle('std.code.lines.code', 'lines of code per file', 'lightblue', 'blue', 8)
);

DiagramStyles.set('std.code.filelines.comments',
    new DiagramStyle('std.code.filelines.comments', 'lines of comment per file', 'lightgreen', 'green', 7)
);

