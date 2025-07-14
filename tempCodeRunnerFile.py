def next_frame(self):
        if self.cap and self.is_playing:
            ret, frame = self.cap.read()
            if not ret:
                self.timer.stop()
                self.cap.release()
                self.is_playing = False
                return

            frame_display = cv2.resize(frame, (self.video_label.width(), self.video_label.height()), interpolation=cv2.INTER_CUBIC)

            input_frame = cv2.resize(frame, (128, 128), interpolation=cv2.INTER_CUBIC)
            input_frame = np.expand_dims(input_frame, axis=0)
            result = self.model.predict(input_frame)[0]
            result = (result * 255).astype(np.uint8)
            result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)

            result_resized = cv2.resize(result, (self.video_label.width(), self.video_label.height()), interpolation=cv2.INTER_CUBIC)

            edges = cv2.Canny(result_resized, 100, 200)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                cv2.drawContours(overlay_frame, contours, -1, (0, 255, 0), 2)

            overlay_frame = cv2.addWeighted(frame_display, 0.7, result_resized, 0.3, 0.0)

            overlay_frame = cv2.cvtColor(overlay_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = overlay_frame.shape
            qimg = QImage(overlay_frame.data, w, h, ch * w, QImage.Format_RGB888)
            margin = 10  
            size = self.label.size()
            scaled_size = QSize(size.width() - margin * 2, size.height() - margin * 2)
            pixmap = QPixmap.fromImage(qimg).scaled(
                scaled_size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation
            )
            self.video_label.setPixmap(pixmap)