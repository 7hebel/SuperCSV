from modules import parser


def parse_string(content: str) -> parser.SCSVObject:
    """ Parse input string, further changes will be saved to this object. """
    return parser._parse(content)

def use_file(fp: str) -> parser.SCSVObject:
    """ Parse input file and save further changes to it. """
    with open(fp, "r") as file:
        raw_content = file.read()
    return parser._parse(raw_content, fp)        
