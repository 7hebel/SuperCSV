class ParseError(Exception):
    """
    Raised when couldn't parse input data.
    """
    
class AnnotationCoverageError(Exception):
    """
    Raised when an field is not annotated or annotated invalid field.
    """
    
class UpdateError(Exception):
    """
    Raised as a result of invalid input data for row update request.
    """