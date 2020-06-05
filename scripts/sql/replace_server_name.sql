SELECT Replace(json::text, 'http://127.0.0.1:5000', 'http://127.0.0.1:8080')::jsonb
FROM records_metadata;
