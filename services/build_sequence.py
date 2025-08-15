def generate_yoga_class(style, muscles, duration):
    """Generate yoga class using the new SequenceBuilder."""
    from services.sequence_builder import SequenceBuilder, SequenceRequest
    
    print(f"DEBUG: Generating class with style='{style}', muscles={muscles}, duration={duration}")
    
    # Create the request
    request = SequenceRequest(
        style=style,
        target_muscles=muscles,
        duration=duration
    )
    
    # Generate using new builder
    builder = SequenceBuilder()
    
    print(f"DEBUG: Available styles: {builder.available_styles}")
    print(f"DEBUG: Available muscles: {builder.available_muscles}")
    
    result = builder.generate_sequence(request)
    
    print(f"DEBUG: Total duration: {result.total_duration}")
    
    # Return in format expected by existing UI
    return {
        "sequences": result.sequences,
        "duration": result.total_duration,
        "muscles": result.muscles_covered
    }