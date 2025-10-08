ax_line = self.line_graph.figure.add_subplot(111)
            if has_raw_data:
                sns.lineplot(data=self.df_raw_data, x="Timestamp", y="X", hue="Area Name", ax=ax_line)
                ax_line.set_title("x position per time")
                ax_line.set_xlabel("Time (seconds)")
                ax_line.set_ylabel("X position")
            else:
                ax_line.text(0.5, 0.5, "No data available\nOr invalid data", ha='center', va='center', fontsize=14)
                ax_line.set_axis_off()
            self.line_graph.figure.tight_layout()