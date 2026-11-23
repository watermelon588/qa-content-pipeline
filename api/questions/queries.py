"""What we search for. Every question source uses the same list.

Keep the phrases short: on Stack Exchange a long phrase like "GPU cloud rental cost" returned nothing
when we tried it (2026-11-22), while "cloud GPU" returned results.
Each phrase costs one request per site, and Stack Exchange allows only ~300 a day without an app key.
"""
QUERIES = ["cloud GPU", "rent GPU", "GPU server"]
