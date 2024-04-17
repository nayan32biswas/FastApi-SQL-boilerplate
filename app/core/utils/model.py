def update_model(target_model, source_model):
    # Update any model from pydantic model

    source_data = source_model.model_dump(exclude_unset=True)

    for key, value in source_data.items():
        setattr(target_model, key, value)

    return target_model
