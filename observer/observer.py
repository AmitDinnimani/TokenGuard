import json
import os
try:
    from .operations import *
except ImportError:
    from operations import *

class TokenObserver:
    def __init__(self):
        self.original_tokens = 0
        self.final_input_tokens = 0
        self.output_tokens = 0
        self.attempts = 0
        self.compression_used = None
        self.successful_compressions = 0
        self.failed_compressions = 0

    def track_original_tokens(self, tokens_len):
        self.original_tokens += tokens_len

    def track_final_input_tokens(self, tokens_len):
        self.final_input_tokens += tokens_len

    def track_output_tokens(self, tokens_len):
        self.output_tokens += tokens_len

    def track_attempts(self, attempts):
        self.attempts += attempts

    def track_compression_used(self, compression_used):
        self.compression_used = compression_used

    def build_request_report(self):
        return {
            "original_tokens": self.original_tokens,
            "final_input_tokens": self.final_input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": calculate_total_tokens(self.final_input_tokens, self.output_tokens),
            "attempts": self.attempts,
            "compression_used": self.compression_used,
            "successful_compressions": self.successful_compressions,
            "failed_compressions": self.failed_compressions
        }

    def save_metadata(self):
        current_report = self.build_request_report()
        new_metadata = generate_updated_metadata(current_report)

        with open("metadata.json", "w") as metadata_file:
            json.dump(new_metadata, metadata_file, indent=4)
    
    def save_request_log(self):
        file_path = "request-log.json"
        
        request_log = {"requests": []}
        if os.path.exists(file_path):
            with open(file_path, "r") as request_log_file:
                try:
                    request_log = json.load(request_log_file)
                except json.JSONDecodeError:
                    pass

        request_log.setdefault("requests", []).append(self.build_request_report())

        with open(file_path, "w") as request_log_file:
            json.dump(request_log, request_log_file, indent=4)

    def save_all_data(self):
        self.save_metadata()
        self.save_request_log()

    def reset(self):
        self.original_tokens = 0
        self.final_input_tokens = 0
        self.output_tokens = 0
        self.attempts = 0
        self.compression_used = None
        self.successful_compressions = 0
        self.failed_compressions = 0