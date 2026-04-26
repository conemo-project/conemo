-- Autor: Ricardo Ceneviva
-- Data: 2026-04-26
-- Projeto: CONEMO

Table conemo-412202:firestore_curated.cur_score_current_v1

                                             Query                                             
 --------------------------------------------------------------------------------------------- 
  WITH user_form_scores AS (                                                                   
                                                                                               
    -- Extração do escore PHQ do primeiro formulário do usuário                                
    SELECT                                                                                     
      document_id                                                AS participant_master_id,     
      document_id                                                AS source_document_id,        
      'PHQ'                                                      AS score_type,                
                                                                                               
      -- score_value: STRING → FLOAT64. Registros não numéricos retornam NULL.                 
      SAFE_CAST(                                                                               
        (SELECT JSON_VALUE(s, '$.score')                                                       
         FROM UNNEST(JSON_EXTRACT_ARRAY(DATA, '$.forms[0].scores')) AS s                       
         WHERE JSON_VALUE(s, '$.type') = 'PHQ'                                                 
         LIMIT 1)                                                                              
        AS FLOAT64                                                                             
      )                                                          AS score_value,               
                                                                                               
      -- Data de referência: timestamp do primeiro formulário                                  
      TIMESTAMP_SECONDS(                                                                       
        SAFE_CAST(JSON_VALUE(DATA, '$.forms[0].date._seconds') AS INT64)                       
      )                                                          AS score_reference_date,      
                                                                                               
      'FORM_INITIAL'                                             AS score_source               
                                                                                               
    FROM `conemo-412202.firestore_export.users_raw_latest`                                     
    WHERE document_id IS NOT NULL                                                              
      AND JSON_EXTRACT_ARRAY(DATA, '$.forms[0].scores') IS NOT NULL                            
                                                                                               
    UNION ALL                                                                                  
                                                                                               
    -- Extração do escore GAD do primeiro formulário do usuário                                
    SELECT                                                                                     
      document_id,                                                                             
      document_id,                                                                             
      'GAD'                                                      AS score_type,                
                                                                                               
      SAFE_CAST(                                                                               
        (SELECT JSON_VALUE(s, '$.score')                                                       
         FROM UNNEST(JSON_EXTRACT_ARRAY(DATA, '$.forms[0].scores')) AS s                       
         WHERE JSON_VALUE(s, '$.type') = 'GAD'                                                 
         LIMIT 1)                                                                              
        AS FLOAT64                                                                             
      )                                                          AS score_value,               
                                                                                               
      TIMESTAMP_SECONDS(                                                                       
        SAFE_CAST(JSON_VALUE(DATA, '$.forms[0].date._seconds') AS INT64)                       
      )                                                          AS score_reference_date,      
                                                                                               
      'FORM_INITIAL'                                             AS score_source               
                                                                                               
    FROM `conemo-412202.firestore_export.users_raw_latest`                                     
    WHERE document_id IS NOT NULL                                                              
      AND JSON_EXTRACT_ARRAY(DATA, '$.forms[0].scores') IS NOT NULL                            
  ),                                                                                           
                                                                                               
  -- ============================================================================              
  -- FONTE 2: Score de progresso de jornada (journeys_raw_latest.$.score)                      
  -- ============================================================================              
  -- Score agregado por jornada. O tipo é inferido do tipo da jornada.                         
  -- Este é um indicador operacional distinto dos escores de triagem.                          
  journey_scores AS (                                                                          
    SELECT                                                                                     
      JSON_VALUE(path_params, '$.userId')                        AS participant_master_id,     
      document_id                                                AS source_document_id,        
                                                                                               
      -- Tipo do escore de jornada: derivado do tipo da jornada (N5)                           
      CASE                                                                                     
        WHEN UPPER(JSON_VALUE(DATA, '$.type')) IN ('GAD', 'ANXIETY') THEN 'GAD_JOURNEY'        
        WHEN UPPER(JSON_VALUE(DATA, '$.type')) IN ('PHQ', 'DEPRESSION',                        
             'DEPRESSAO', 'DEPRESSÃO')                          THEN 'PHQ_JOURNEY'             
        ELSE 'OTHER_JOURNEY'                                                                   
      END                                                        AS score_type,                
                                                                                               
      -- score_value: score agregado da jornada (FLOAT64)                                      
      SAFE_CAST(JSON_VALUE(DATA, '$.score') AS FLOAT64)          AS score_value,               
                                                                                               
      -- score_reference_date: proxy via lastAccess (melhor disponível nesta fonte)            
      TIMESTAMP_SECONDS(                                                                       
        SAFE_CAST(JSON_VALUE(DATA, '$.lastAccess._seconds') AS INT64)                          
      )                                                          AS score_reference_date,      
                                                                                               
      'JOURNEY_AGGREGATE'                                        AS score_source               
                                                                                               
    FROM `conemo-412202.firestore_export.journeys_raw_latest`                                  
    WHERE JSON_VALUE(DATA, '$.score') IS NOT NULL                                              
      AND JSON_VALUE(path_params, '$.userId') IS NOT NULL                                      
      AND TRIM(JSON_VALUE(path_params, '$.userId')) != ''                                      
  ),                                                                                           
                                                                                               
  -- ============================================================================              
  -- UNIÃO DAS FONTES                                                                          
  -- ============================================================================              
  -- Combinamos os escores de formulário com os scores de jornada.                             
  -- A distinção de score_source permite filtragem posterior.                                  
  all_scores AS (                                                                              
    SELECT * FROM user_form_scores                                                             
    WHERE score_value IS NOT NULL  -- Excluir escores sem valor calculável                     
                                                                                               
    UNION ALL                                                                                  
                                                                                               
    SELECT                                                                                     
      participant_master_id,                                                                   
      source_document_id,                                                                      
      score_type,                                                                              
      score_value,                                                                             
      score_reference_date,                                                                    
      score_source                                                                             
    FROM journey_scores                                                                        
  ),                                                                                           
                                                                                               
  -- ============================================================================              
  -- DERIVAÇÃO DE score_quality_flag                                                           
  -- ============================================================================              
  scores_with_quality AS (                                                                     
    SELECT                                                                                     
      participant_master_id,                                                                   
      source_document_id,                                                                      
      'RESOLVED_DOCUMENT'                                        AS id_reconciliation_status,  
      score_type,                                                                              
      score_value,                                                                             
      score_reference_date,                                                                    
      score_source,                                                                            
                                                                                               
      -- Regras de qualidade do escore:                                                        
      --   FAIL → score_value nulo (escore ausente ou não parseável)                           
      --   WARN → score presente mas data de referência ausente                                
      --   OK   → score e data de referência disponíveis                                       
      CASE                                                                                     
        WHEN score_value IS NULL               THEN 'FAIL'                                     
        WHEN score_reference_date IS NULL      THEN 'WARN'                                     
        ELSE 'OK'                                                                              
      END                                                        AS score_quality_flag         
                                                                                               
    FROM all_scores                                                                            
  )                                                                                            
                                                                                               
  -- ============================================================================              
  -- RESULTADO FINAL                                                                           
  -- ============================================================================              
  -- Uma linha por participant_master_id × score_type × score_reference_date.                  
  -- A distinção de score_source permite análise separada por tipo de origem.                  
  SELECT                                                                                       
    participant_master_id,                                                                     
    source_document_id,                                                                        
    id_reconciliation_status,                                                                  
    score_type,                                                                                
    score_value,                                                                               
    score_reference_date,                                                                      
    score_source,                                                                              
    score_quality_flag                                                                         
                                                                                               
  FROM scores_with_quality                                                                     
  WHERE participant_master_id IS NOT NULL                                                      
