import tensorflow as tf


def _compile(model: tf.keras.Model) -> tf.keras.Model:
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.Precision(), tf.keras.metrics.Recall()],
    )
    return model


def _cnn_small(input_shape: tuple[int, int, int]) -> tf.keras.Model:
    inputs = tf.keras.Input(shape=input_shape)
    x = inputs
    for filters in (16, 32, 64):
        x = tf.keras.layers.Conv2D(filters, (3, 3), padding="same", activation="relu")(x)
        x = tf.keras.layers.MaxPooling2D((2, 2))(x)
        x = tf.keras.layers.Dropout(0.2)(x)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(64, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)
    return _compile(tf.keras.Model(inputs=inputs, outputs=outputs))


def _cnn_tiny(input_shape: tuple[int, int, int]) -> tf.keras.Model:
    inputs = tf.keras.Input(shape=input_shape)
    x = tf.keras.layers.Conv2D(8, (3, 3), padding="same", activation="relu")(inputs)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)
    x = tf.keras.layers.Conv2D(16, (3, 3), padding="same", activation="relu")(x)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)
    return _compile(tf.keras.Model(inputs=inputs, outputs=outputs))


def _linear_head(input_shape: tuple[int, int, int]) -> tf.keras.Model:
    inputs = tf.keras.Input(shape=input_shape)
    x = tf.keras.layers.GlobalAveragePooling2D()(inputs)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)
    return _compile(tf.keras.Model(inputs=inputs, outputs=outputs))


def build_model(input_shape: tuple[int, int, int], model_type: str = "cnn_small") -> tf.keras.Model:
    if model_type == "cnn_small":
        return _cnn_small(input_shape)
    if model_type == "cnn_tiny":
        return _cnn_tiny(input_shape)
    if model_type == "linear":
        return _linear_head(input_shape)
    raise ValueError(f"Unknown model_type: {model_type}")
