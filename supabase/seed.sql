-- Insert 50 dummy backstories embedded with rich personas
DO $$
DECLARE
    i INT;
    names TEXT[] := ARRAY['James', 'Sarah', 'Robert', 'Emily', 'Michael', 'Jessica', 'William', 'Ashley', 'David', 'Jennifer'];
    parties TEXT[] := ARRAY['Republican', 'Democrat', 'Independent', 'Libertarian', 'Green'];
    ages TEXT[] := ARRAY['18-24', '25-34', '35-44', '45-54', '55-64', '65+'];
    genders TEXT[] := ARRAY['Male', 'Female', 'Non-binary'];

    v_name TEXT;
    v_party TEXT;
    v_age TEXT;
    v_gender TEXT;
    v_content TEXT;
    v_demographics JSONB;
BEGIN
    FOR i IN 1..50 LOOP
        -- Random selection
        v_name := names[1 + floor(random() * array_length(names, 1))::int];
        v_party := parties[1 + floor(random() * array_length(parties, 1))::int];
        v_age := ages[1 + floor(random() * array_length(ages, 1))::int];
        v_gender := genders[1 + floor(random() * array_length(genders, 1))::int];

        v_demographics := jsonb_build_object(
            'age', v_age,
            'gender', v_gender,
            'political_party', v_party
        );

        v_content := format('Interview with %s.
        Q: Tell me about yourself.
        A: Hi, I''m %s. I identify as a %s %s and I usually vote %s. I grew up in a small town...
        Q: What are your thoughts on technology?
        A: I think it''s moving too fast...', v_name, v_name, v_age, v_gender, v_party);

        INSERT INTO public.backstories (content, model_signature, demographics, custom_tags)
        VALUES (
            v_content,
            'Seed-Generator-v1',
            v_demographics,
            '{}'::jsonb
        );
    END LOOP;
END $$;
