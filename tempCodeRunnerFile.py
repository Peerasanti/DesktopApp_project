def sanitize_filename(self,filename):
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, '_', filename)
        sanitized = sanitized.strip().strip('.')
        return sanitized
    
    def _write_csv(self, data, output_file, headers):
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                for row in data:
                    writer.writerow(row)
        except OSError as e:
            print(f"Error writing to CSV file {output_file}: {e}")
            raise
    
    def export_to_csv(self):
        if not self.area_summary and not self.raw_data:
            print("Not found area summary and rawdata")
            return
        
        if self.area_summary :
            summary_file = os.path.join('export', f"{self.current_experiment_date}_{self.current_experiment_name}_area_summary.csv")
            summary_area_file = self.sanitize_filename(summary_file)
            summary_headers = ['area_id', 'experiment_id', 'area_name', 'color', 'hit_count', 'total_time', 'area_point']
            self._write_csv(self.area_summary, summary_area_file, summary_headers)
            print(f"Exported area_summary to {summary_file}")

        if self.raw_data:
            rawdata_file = os.path.join('export', f"{self.current_experiment_date}_{self.current_experiment_name}_raw_data.csv")
            rawdata_name_file = self.sanitize_filename(rawdata_file)
            rawdata_headers = ['experiment_id', 'area_id', 'timestamp', 'frame_count', 'area_name', 'rat_position_x', 'rat_position_y']
            self._write_csv(self.raw_data, rawdata_name_file, rawdata_headers)
            print(f"Exported raw_data to {rawdata_file}")