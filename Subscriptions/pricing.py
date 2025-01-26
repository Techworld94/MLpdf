import fitz

class PricingValidator:
    SUBSCRIPTION_LIMITS = {
        "Free": {
            "max_files": 1,
            "max_file_size_mb": 2,
            "max_pages": 1
        },
        "Basic": {
            "max_files": 5,
            "max_file_size_mb": 10,
            "max_pages": 50
        },
        "Standard": {
            "max_files": 5,
            "max_file_size_mb": 50,
            "max_pages": 200
        },
        "Plus": {
            "max_files": float("inf"),
            "max_file_size_mb": float("inf"),
            "max_pages": float("inf")
        }
    }

    def __init__(self, subscription_type):
        self.subscription_type = subscription_type
        self.limits = self.SUBSCRIPTION_LIMITS.get(subscription_type, {})

    def validate_file_count(self, file_count):
        """Validate the number of files uploaded."""
        max_files = self.limits.get("max_files", float("inf"))
        if file_count > max_files:
            return False, f"❌ Only {max_files} files are allowed for {self.subscription_type} users."
        return True, None

    def validate_file_size(self, file):
        """Validate the size of an uploaded file."""
        max_file_size_mb = self.limits.get("max_file_size_mb", float("inf"))
        file_size_mb = len(file.read()) / (1024 * 1024)
        file.seek(0)
        if file_size_mb > max_file_size_mb:
            return False, f"❌ File size exceeds {max_file_size_mb} MB limit for {self.subscription_type} users."
        return True, None

    def validate_page_count(self, file):
        """Validate the number of pages in an uploaded PDF."""
        max_pages = self.limits.get("max_pages", float("inf"))
        try:
            with fitz.open(stream=file, filetype="pdf") as pdf:
                if len(pdf) > max_pages:
                    return False, f"❌ File exceeds {max_pages} page limit for {self.subscription_type} users."
        except Exception as e:
            return False, f"❌ Error reading PDF: {str(e)}"
        return True, None
