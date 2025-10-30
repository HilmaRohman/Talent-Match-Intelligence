-- ===========================================
-- TALENT BENCHMARK MATCHING ALGORITHM - ML-DRIVEN WEIGHTS
-- ===========================================

-- Step 1: Benchmark Configuration
-- Defines the target job role and selects top performers as benchmark
WITH benchmark_config AS (
    SELECT 
        'VACANCY_001' AS job_vacancy_id,
        'Senior Strategy Manager' AS role_name,
        'Level 9' AS job_level,
        'Lead strategic initiatives and drive business growth through data-driven insights' AS role_purpose,
        
        -- Select top 5 employees with highest performance ratings as benchmark talent pool
        ARRAY(
            SELECT employee_id 
            FROM performance_yearly 
            WHERE rating IS NOT NULL
            ORDER BY rating DESC 
            LIMIT 5
        ) AS selected_talent_ids
),

-- Step 2: ML-Driven Talent Variables Configuration
-- Defines weights for each talent variable based on machine learning feature importance analysis
talent_variables_config AS (
    SELECT *
    FROM (VALUES
        -- Format: (tv_name, tgv_name, tv_weight, tgv_weight, is_higher_better)
        -- COGNITIVE: 3.9% total weight from ML analysis
        ('IQ', 'COGNITIVE', 0.014, 0.039, true),      -- 1.4% from ML feature importance
        ('GTQ', 'COGNITIVE', 0.025, 0.039, true),     -- 2.5% from ML feature importance
        
        -- PERFORMANCE: 15% weight (assumption from benchmark selection)
        ('PERFORMANCE', 'PERFORMANCE', 1.0, 0.15, true),
        
        -- COMPETENCY: 64.6% total weight - MOST IMPORTANT from ML analysis
        ('COMPETENCY_VCU', 'COMPETENCY', 0.067, 0.646, true),  -- 6.7% - Top feature
        ('COMPETENCY_GDR', 'COMPETENCY', 0.062, 0.646, true),  -- 6.2%
        ('COMPETENCY_SEA', 'COMPETENCY', 0.060, 0.646, true),  -- 6.0%
        ('COMPETENCY_CSI', 'COMPETENCY', 0.058, 0.646, true),  -- 5.8%
        ('COMPETENCY_LIE', 'COMPETENCY', 0.057, 0.646, true),  -- 5.7%
        ('COMPETENCY_IDS', 'COMPETENCY', 0.057, 0.646, true),  -- 5.7%
        ('COMPETENCY_QDD', 'COMPETENCY', 0.057, 0.646, true),  -- 5.7%
        ('COMPETENCY_STO', 'COMPETENCY', 0.053, 0.646, true),  -- 5.3%
        ('COMPETENCY_FTC', 'COMPETENCY', 0.049, 0.646, true),  -- 4.9%
        ('COMPETENCY_CEX', 'COMPETENCY', 0.046, 0.646, true),  -- 4.6%
        
        -- WORK EFFICIENCY: 12.1% total weight from ML
        ('PAULI', 'WORK_EFFICIENCY', 0.082, 0.121, true),     -- 8.2% from ML
        ('FAXTOR', 'WORK_EFFICIENCY', 0.039, 0.121, true),    -- 3.9% from ML
        
        -- BEHAVIORAL: 15.1% total weight from ML  
        ('DISC_D', 'BEHAVIORAL', 0.050, 0.151, true),         -- Estimated
        ('DISC_I', 'BEHAVIORAL', 0.050, 0.151, true),         -- Estimated
        ('WOO', 'BEHAVIORAL', 0.060, 0.151, true),            -- 6.0% from ML
        ('DEVELOPER', 'BEHAVIORAL', 0.055, 0.151, true),      -- 5.5% from ML
        ('COMMUNICATION', 'BEHAVIORAL', 0.036, 0.151, true),  -- 3.6% from ML
        
        -- EXPERIENCE: 4.3% total weight from ML
        ('EXPERIENCE', 'EXPERIENCE', 1.0, 0.043, true)
    ) AS config(tv_name, tgv_name, tv_weight, tgv_weight, is_higher_better)
),

-- Step 3: Parse Benchmark Talent IDs
-- Convert array of benchmark employee IDs into individual rows for querying
top_performers AS (
    SELECT UNNEST(selected_talent_ids) AS benchmark_employee_id
    FROM benchmark_config
    WHERE CARDINALITY(selected_talent_ids) > 0
),

-- Step 4: Calculate Baseline Scores from Benchmark Talent
-- Compute median scores for each talent variable using top performers as reference
calculated_baselines AS (
    -- Baseline for Competency VCU (Top ML feature)
    SELECT 
        'COMPETENCY_VCU' AS tv_name,
        'COMPETENCY' AS tgv_name,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY score) AS baseline_score
    FROM competencies_yearly
    WHERE employee_id IN (SELECT benchmark_employee_id FROM top_performers)
        AND pillar_code = 'VCU'
    
    UNION ALL
    
    -- Baseline for Competency GDR (Second top ML feature)
    SELECT 
        'COMPETENCY_GDR' AS tv_name,
        'COMPETENCY' AS tgv_name,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY score) AS baseline_score
    FROM competencies_yearly
    WHERE employee_id IN (SELECT benchmark_employee_id FROM top_performers)
        AND pillar_code = 'GDR'
    
    UNION ALL
    
    -- Baseline for Competency SEA (Third top ML feature)
    SELECT 
        'COMPETENCY_SEA' AS tv_name,
        'COMPETENCY' AS tgv_name,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY score) AS baseline_score
    FROM competencies_yearly
    WHERE employee_id IN (SELECT benchmark_employee_id FROM top_performers)
        AND pillar_code = 'SEA'
    
    UNION ALL
    
    -- Baseline for Competency CSI
    SELECT 
        'COMPETENCY_CSI' AS tv_name,
        'COMPETENCY' AS tgv_name,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY score) AS baseline_score
    FROM competencies_yearly
    WHERE employee_id IN (SELECT benchmark_employee_id FROM top_performers)
        AND pillar_code = 'CSI'
    
    UNION ALL
    
    -- Baseline for Competency LIE
    SELECT 
        'COMPETENCY_LIE' AS tv_name,
        'COMPETENCY' AS tgv_name,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY score) AS baseline_score
    FROM competencies_yearly
    WHERE employee_id IN (SELECT benchmark_employee_id FROM top_performers)
        AND pillar_code = 'LIE'
    
    UNION ALL
    
    -- Baseline for Competency IDS
    SELECT 
        'COMPETENCY_IDS' AS tv_name,
        'COMPETENCY' AS tgv_name,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY score) AS baseline_score
    FROM competencies_yearly
    WHERE employee_id IN (SELECT benchmark_employee_id FROM top_performers)
        AND pillar_code = 'IDS'
    
    UNION ALL
    
    -- Baseline for Cognitive (IQ) - Lower weight from ML
    SELECT 
        'IQ' AS tv_name,
        'COGNITIVE' AS tgv_name,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY iq) AS baseline_score
    FROM profiles_psych
    WHERE employee_id IN (SELECT benchmark_employee_id FROM top_performers)
        AND iq IS NOT NULL
    
    UNION ALL
    
    -- Baseline for Cognitive (GTQ) - Higher weight from ML
    SELECT 
        'GTQ' AS tv_name,
        'COGNITIVE' AS tgv_name,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY gtq) AS baseline_score
    FROM profiles_psych
    WHERE employee_id IN (SELECT benchmark_employee_id FROM top_performers)
        AND gtq IS NOT NULL
    
    UNION ALL
    
    -- Baseline for Performance
    SELECT 
        'PERFORMANCE' AS tv_name,
        'PERFORMANCE' AS tgv_name,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY rating) AS baseline_score
    FROM performance_yearly
    WHERE employee_id IN (SELECT benchmark_employee_id FROM top_performers)
    
    UNION ALL
    
    -- Baseline for Work Efficiency (Pauli) - High weight from ML
    SELECT 
        'PAULI' AS tv_name,
        'WORK_EFFICIENCY' AS tgv_name,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pauli) AS baseline_score
    FROM profiles_psych
    WHERE employee_id IN (SELECT benchmark_employee_id FROM top_performers)
        AND pauli IS NOT NULL
    
    UNION ALL
    
    -- Baseline for Work Efficiency (Faxtor)
    SELECT 
        'FAXTOR' AS tv_name,
        'WORK_EFFICIENCY' AS tgv_name,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY faxtor) AS baseline_score
    FROM profiles_psych
    WHERE employee_id IN (SELECT benchmark_employee_id FROM top_performers)
        AND faxtor IS NOT NULL
    
    UNION ALL
    
    -- Baseline for Experience
    SELECT 
        'EXPERIENCE' AS tv_name,
        'EXPERIENCE' AS tgv_name,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY years_of_service_months) AS baseline_score
    FROM employees
    WHERE employee_id IN (SELECT benchmark_employee_id FROM top_performers)
),

-- Step 5: Combine Baselines with ML-Driven Weights
-- Merge calculated baseline scores with their corresponding ML weights
manager_selection AS (
    SELECT 
        cb.tv_name,
        cb.tgv_name,
        cb.baseline_score,
        tvc.tv_weight,
        tvc.tgv_weight,
        tvc.is_higher_better
    FROM calculated_baselines cb
    INNER JOIN talent_variables_config tvc ON cb.tv_name = tvc.tv_name AND cb.tgv_name = tvc.tgv_name
    WHERE cb.baseline_score IS NOT NULL
),

-- Step 6: Employee Base Information
-- Retrieve core employee data with organizational hierarchy details
employee_base AS (
    SELECT 
        e.employee_id,
        e.fullname,
        d.name AS directorate,
        p.name AS position,
        g.name AS grade,
        e.years_of_service_months
    FROM employees e
    LEFT JOIN dim_directorates d ON e.directorate_id = d.directorate_id
    LEFT JOIN dim_positions p ON e.position_id = p.position_id
    LEFT JOIN dim_grades g ON e.grade_id = g.grade_id
    WHERE e.employee_id IS NOT NULL
),

-- Step 7: Psychological Profile Data Preparation
-- Gather cognitive and behavioral assessment data with null handling
psych_data AS (
    SELECT 
        employee_id,
        COALESCE(iq, 0) AS iq,
        COALESCE(gtq, 0) AS gtq,
        COALESCE(pauli, 0) AS pauli,
        COALESCE(faxtor, 0) AS faxtor,
        disc,
        mbti
    FROM profiles_psych
),

-- Step 8: Performance Data Preparation
-- Calculate average performance ratings for each employee
performance_data AS (
    SELECT 
        employee_id,
        AVG(rating) AS avg_performance_rating
    FROM performance_yearly
    GROUP BY employee_id
),

-- Step 9: Competency Data Preparation
-- Aggregate competency scores by pillar for the most recent year
competency_data AS (
    SELECT 
        employee_id,
        pillar_code,
        AVG(score) AS avg_competency_score
    FROM competencies_yearly
    WHERE year = (SELECT MAX(year) FROM competencies_yearly)
    GROUP BY employee_id, pillar_code
),

-- Step 10: Behavioral Strengths Data Preparation
-- Compile top 5 strengths for each employee for behavioral analysis
strengths_data AS (
    SELECT 
        employee_id,
        STRING_AGG(theme, ', ' ORDER BY rank) AS top_strengths,
        COUNT(*) AS strengths_count
    FROM strengths
    WHERE rank <= 5
    GROUP BY employee_id
),

-- Step 11: Talent Variable (TV) Match Rate Calculation
-- Calculate how closely each employee matches each talent variable benchmark
tv_match_rates AS (
    SELECT 
        eb.employee_id,
        eb.directorate,
        eb.position AS role,
        eb.grade,
        ms.tgv_name,
        ms.tv_name,
        ms.baseline_score,
        ms.tv_weight,
        ms.tgv_weight,
        ms.is_higher_better,
        
        -- Extract user score based on talent variable type
        CASE 
            -- Cognitive variables
            WHEN ms.tv_name = 'IQ' THEN COALESCE(ps.iq, 0)
            WHEN ms.tv_name = 'GTQ' THEN COALESCE(ps.gtq, 0)
            WHEN ms.tv_name = 'PAULI' THEN COALESCE(ps.pauli, 0)
            WHEN ms.tv_name = 'FAXTOR' THEN COALESCE(ps.faxtor, 0)
            
            -- Performance
            WHEN ms.tv_name = 'PERFORMANCE' THEN COALESCE(pd.avg_performance_rating, 0)
            
            -- Experience
            WHEN ms.tv_name = 'EXPERIENCE' THEN eb.years_of_service_months
            
            -- Competencies (prioritize top ML features)
            WHEN ms.tv_name = 'COMPETENCY_VCU' THEN (
                SELECT COALESCE(avg_competency_score, 0) 
                FROM competency_data cd 
                WHERE cd.employee_id = eb.employee_id 
                AND cd.pillar_code = 'VCU'
            )
            WHEN ms.tv_name = 'COMPETENCY_GDR' THEN (
                SELECT COALESCE(avg_competency_score, 0) 
                FROM competency_data cd 
                WHERE cd.employee_id = eb.employee_id 
                AND cd.pillar_code = 'GDR'
            )
            WHEN ms.tv_name = 'COMPETENCY_SEA' THEN (
                SELECT COALESCE(avg_competency_score, 0) 
                FROM competency_data cd 
                WHERE cd.employee_id = eb.employee_id 
                AND cd.pillar_code = 'SEA'
            )
            WHEN ms.tv_name = 'COMPETENCY_CSI' THEN (
                SELECT COALESCE(avg_competency_score, 0) 
                FROM competency_data cd 
                WHERE cd.employee_id = eb.employee_id 
                AND cd.pillar_code = 'CSI'
            )
            WHEN ms.tv_name = 'COMPETENCY_LIE' THEN (
                SELECT COALESCE(avg_competency_score, 0) 
                FROM competency_data cd 
                WHERE cd.employee_id = eb.employee_id 
                AND cd.pillar_code = 'LIE'
            )
            WHEN ms.tv_name = 'COMPETENCY_IDS' THEN (
                SELECT COALESCE(avg_competency_score, 0) 
                FROM competency_data cd 
                WHERE cd.employee_id = eb.employee_id 
                AND cd.pillar_code = 'IDS'
            )
            
            -- Behavioral (simplified for example)
            WHEN ms.tv_name = 'DISC_D' THEN 
                CASE WHEN ps.disc LIKE 'D%' THEN 1 ELSE 0 END
            WHEN ms.tv_name = 'DISC_I' THEN 
                CASE WHEN ps.disc LIKE 'I%' THEN 1 ELSE 0 END
            WHEN ms.tv_name = 'WOO' THEN 
                CASE WHEN sd.top_strengths LIKE '%Woo%' THEN 1 ELSE 0 END
            WHEN ms.tv_name = 'DEVELOPER' THEN 
                CASE WHEN sd.top_strengths LIKE '%Developer%' THEN 1 ELSE 0 END
            WHEN ms.tv_name = 'COMMUNICATION' THEN 
                CASE WHEN sd.top_strengths LIKE '%Communication%' THEN 1 ELSE 0 END
            
            ELSE 0
        END AS user_score,
        
        -- Calculate TV Match Rate based on variable type
        CASE 
            -- For numerical variables where higher is better
            WHEN ms.is_higher_better = true AND ms.tv_name NOT LIKE 'DISC_%' AND ms.tv_name NOT IN ('WOO', 'DEVELOPER', 'COMMUNICATION') THEN
                CASE 
                    WHEN ms.baseline_score > 0 THEN 
                        -- Formula: (user_score / baseline_score) * 100, maximum 100%
                        LEAST(
                            (COALESCE(
                                CASE 
                                    WHEN ms.tv_name = 'IQ' THEN ps.iq
                                    WHEN ms.tv_name = 'GTQ' THEN ps.gtq
                                    WHEN ms.tv_name = 'PAULI' THEN ps.pauli
                                    WHEN ms.tv_name = 'FAXTOR' THEN ps.faxtor
                                    WHEN ms.tv_name = 'PERFORMANCE' THEN pd.avg_performance_rating
                                    WHEN ms.tv_name = 'EXPERIENCE' THEN eb.years_of_service_months
                                    WHEN ms.tv_name = 'COMPETENCY_VCU' THEN (
                                        SELECT avg_competency_score 
                                        FROM competency_data cd 
                                        WHERE cd.employee_id = eb.employee_id 
                                        AND cd.pillar_code = 'VCU'
                                    )
                                    WHEN ms.tv_name = 'COMPETENCY_GDR' THEN (
                                        SELECT avg_competency_score 
                                        FROM competency_data cd 
                                        WHERE cd.employee_id = eb.employee_id 
                                        AND cd.pillar_code = 'GDR'
                                    )
                                    WHEN ms.tv_name = 'COMPETENCY_SEA' THEN (
                                        SELECT avg_competency_score 
                                        FROM competency_data cd 
                                        WHERE cd.employee_id = eb.employee_id 
                                        AND cd.pillar_code = 'SEA'
                                    )
                                    WHEN ms.tv_name = 'COMPETENCY_CSI' THEN (
                                        SELECT avg_competency_score 
                                        FROM competency_data cd 
                                        WHERE cd.employee_id = eb.employee_id 
                                        AND cd.pillar_code = 'CSI'
                                    )
                                    WHEN ms.tv_name = 'COMPETENCY_LIE' THEN (
                                        SELECT avg_competency_score 
                                        FROM competency_data cd 
                                        WHERE cd.employee_id = eb.employee_id 
                                        AND cd.pillar_code = 'LIE'
                                    )
                                    WHEN ms.tv_name = 'COMPETENCY_IDS' THEN (
                                        SELECT avg_competency_score 
                                        FROM competency_data cd 
                                        WHERE cd.employee_id = eb.employee_id 
                                        AND cd.pillar_code = 'IDS'
                                    )
                                    ELSE 0
                                END, 0
                            ) / ms.baseline_score) * 100, 
                            100
                        )
                    ELSE 0
                END
            
            -- For categorical variables (exact match = 100%, no match = 0%)
            WHEN ms.tv_name LIKE 'DISC_%' OR ms.tv_name IN ('WOO', 'DEVELOPER', 'COMMUNICATION') THEN
                CASE 
                    WHEN (ms.tv_name = 'DISC_D' AND ps.disc LIKE 'D%') OR
                         (ms.tv_name = 'DISC_I' AND ps.disc LIKE 'I%') OR
                         (ms.tv_name = 'WOO' AND sd.top_strengths LIKE '%Woo%') OR
                         (ms.tv_name = 'DEVELOPER' AND sd.top_strengths LIKE '%Developer%') OR
                         (ms.tv_name = 'COMMUNICATION' AND sd.top_strengths LIKE '%Communication%')
                    THEN 100.0
                    ELSE 0.0
                END
            
            ELSE 0
        END AS tv_match_rate
        
    FROM employee_base eb
    CROSS JOIN manager_selection ms
    LEFT JOIN psych_data ps ON eb.employee_id = ps.employee_id
    LEFT JOIN performance_data pd ON eb.employee_id = pd.employee_id
    LEFT JOIN strengths_data sd ON eb.employee_id = sd.employee_id
    WHERE eb.employee_id NOT IN (SELECT benchmark_employee_id FROM top_performers)  -- Exclude benchmark employees from candidates
),

-- Step 12: Talent Group Variable (TGV) Match Rate Calculation
-- Calculate weighted average match rates for each talent group (cognitive, competency, etc.)
tgv_match_rates AS (
    SELECT 
        employee_id,
        directorate,
        role,
        grade,
        tgv_name,
        -- Calculate weighted average for TGV match rate using ML-driven TV weights
        CASE 
            WHEN SUM(tv_weight) > 0 THEN 
                SUM(tv_match_rate * tv_weight) / SUM(tv_weight)
            ELSE 0 
        END AS tgv_match_rate,
        -- Use TGV weight from ML-driven config
        MAX(tgv_weight) AS tgv_weight,
        COUNT(*) AS tv_count_in_tgv
    FROM tv_match_rates
    GROUP BY employee_id, directorate, role, grade, tgv_name
),

-- Step 13: Final Match Rate Calculation
-- Compute overall weighted match rate across all talent groups
final_match_rates AS (
    SELECT 
        tmr.employee_id,
        tmr.directorate,
        tmr.role,
        tmr.grade,
        -- Calculate weighted average final match rate using ML-driven TGV weights
        CASE 
            WHEN SUM(tmr.tgv_weight) > 0 THEN 
                SUM(tmr.tgv_match_rate * tmr.tgv_weight) / SUM(tmr.tgv_weight)
            ELSE AVG(tmr.tgv_match_rate)
        END AS final_match_rate,
        COUNT(*) AS tgv_count
    FROM tgv_match_rates tmr
    GROUP BY tmr.employee_id, tmr.directorate, tmr.role, tmr.grade
)

-- Step 14: FINAL OUTPUT - Format results according to expected columns
SELECT 
    tv.employee_id,
    tv.directorate,
    tv.role,
    tv.grade,
    tv.tgv_name,
    tv.tv_name,
    ROUND(tv.baseline_score::numeric, 2) AS baseline_score,
    ROUND(tv.user_score::numeric, 2) AS user_score,
    ROUND(tv.tv_match_rate::numeric, 2) AS tv_match_rate,
    ROUND(tgv.tgv_match_rate::numeric, 2) AS tgv_match_rate,
    ROUND(fmr.final_match_rate::numeric, 2) AS final_match_rate,
    eb.fullname,
    eb.years_of_service_months,
    ps.disc,
    ps.mbti,
    pd.avg_performance_rating AS current_performance_rating,
    sd.top_strengths,
    bc.role_name AS benchmark_role_name,
    bc.job_level AS benchmark_level
FROM tv_match_rates tv
INNER JOIN tgv_match_rates tgv ON tv.employee_id = tgv.employee_id AND tv.tgv_name = tgv.tgv_name
INNER JOIN final_match_rates fmr ON tv.employee_id = fmr.employee_id
INNER JOIN employee_base eb ON tv.employee_id = eb.employee_id
CROSS JOIN benchmark_config bc
LEFT JOIN psych_data ps ON tv.employee_id = ps.employee_id
LEFT JOIN performance_data pd ON tv.employee_id = pd.employee_id
LEFT JOIN strengths_data sd ON tv.employee_id = sd.employee_id
WHERE tv.tv_match_rate > 0  -- Only show employees with some level of match
ORDER BY 
    fmr.final_match_rate DESC,  -- Sort by highest match rate first
    tgv.tgv_match_rate DESC,
    tv.tv_match_rate DESC,
    eb.years_of_service_months desc;
--LIMIT 100;  -- Optional limit for result set size