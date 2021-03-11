UPDATE records_metadata
SET    json = Replace(json::text, 'http://127.0.0.1:5000', 'https://repozitar.narodni-repozitar.cz')::jsonb;
-- https://stackoverflow.com/questions/51005106/postgresql-find-and-replace-in-jsonb-data-as-text