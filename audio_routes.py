# Add this to app.py - Audio Recording Routes


@app.route("/api/audio/save", methods=["POST"])
def save_audio_recording():
    """Save voice recording to server."""
    try:
        if "audio" not in request.files:
            return jsonify({"status": "error", "message": "No audio file"}), 400

        audio_file = request.files["audio"]

        if audio_file.filename == "":
            return jsonify({"status": "error", "message": "No file selected"}), 400

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"voice_recording_{timestamp}.webm"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        # Save audio file
        audio_file.save(filepath)

        # Get file size and duration (duration requires additional library)
        file_size = os.path.getsize(filepath)

        # Save to database
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO audio_transcriptions 
                         (audio_filename, transcription_text, created_at) 
                         VALUES (?, ?, ?)""",
            (filename, "", datetime.now().isoformat()),
        )
        db.commit()
        audio_id = cursor.lastrowid

        return jsonify(
            {
                "status": "success",
                "filename": filename,
                "audio_id": audio_id,
                "size": file_size,
            }
        )

    except Exception as e:
        print(f"Error saving audio: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/audio/<filename>", methods=["GET"])
def serve_audio(filename):
    """Serve audio file for playback."""
    try:
        return send_file(
            os.path.join(app.config["UPLOAD_FOLDER"], filename), mimetype="audio/webm"
        )
    except Exception as e:
        print(f"Error serving audio: {e}")
        return jsonify({"status": "error", "message": str(e)}), 404
