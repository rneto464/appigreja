-- ============================================
-- Script SQL para inicializar banco Supabase
-- Execute este script no SQL Editor do Supabase
-- ============================================

-- ============================================
-- 1. CRIAR TABELAS
-- ============================================

-- Tabela de escalas
CREATE TABLE IF NOT EXISTS escalas (
    id SERIAL PRIMARY KEY,
    data VARCHAR(10) NOT NULL,
    tipo_escala VARCHAR(100) NOT NULL,
    bata_cor VARCHAR(50),
    cerimoniarios TEXT,
    veteranos TEXT,
    mirins TEXT,
    turibulo TEXT,
    naveta TEXT,
    tochas TEXT
);

CREATE INDEX IF NOT EXISTS idx_escalas_data ON escalas(data);
CREATE INDEX IF NOT EXISTS idx_escalas_tipo ON escalas(tipo_escala);

-- Tabela de pessoas
CREATE TABLE IF NOT EXISTS pessoas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE,
    grupo VARCHAR(50) NOT NULL,
    funcoes TEXT
);

CREATE INDEX IF NOT EXISTS idx_pessoas_grupo ON pessoas(grupo);

-- Tabela de templates de escala
CREATE TABLE IF NOT EXISTS escala_templates (
    id SERIAL PRIMARY KEY,
    tipo_escala VARCHAR(100) NOT NULL UNIQUE,
    cerimoniarios_template TEXT,
    veteranos_template TEXT,
    mirins_template TEXT,
    turibulo_template TEXT,
    naveta_template TEXT,
    tochas_template TEXT
);

-- Tabela de dias de missa
CREATE TABLE IF NOT EXISTS dias_missa (
    id SERIAL PRIMARY KEY,
    dia_semana INTEGER NOT NULL,
    tipo_escala VARCHAR(100) NOT NULL,
    horario VARCHAR(10),
    ativo INTEGER DEFAULT 1,
    ordem INTEGER DEFAULT 0,
    UNIQUE(dia_semana, tipo_escala)
);

CREATE INDEX IF NOT EXISTS idx_dias_missa_dia ON dias_missa(dia_semana);
CREATE INDEX IF NOT EXISTS idx_dias_missa_ativo ON dias_missa(ativo);

-- ============================================
-- 2. INSERIR PESSOAS
-- ============================================

-- Mestres de Cerimônia (Cerimoniários)
INSERT INTO pessoas (nome, grupo, funcoes) VALUES
('Alejandro', 'cerimoniario', ''),
('João Pedro', 'cerimoniario', ''),
('Pedro Reis', 'cerimoniario', ''),
('Adriano', 'cerimoniario', ''),
('Lucas', 'cerimoniario', ''),
('André', 'cerimoniario', ''),
('Pedro Barroso', 'cerimoniario', '')
ON CONFLICT (nome) DO NOTHING;

-- Experientes (Veteranos)
INSERT INTO pessoas (nome, grupo, funcoes) VALUES
('Ana Julia', 'veterano', ''),
('Vitória', 'veterano', ''),
('Sofia Reis', 'veterano', ''),
('Armando', 'veterano', ''),
('Karla', 'veterano', ''),
('Mateus', 'veterano', ''),
('João Raffael', 'veterano', ''),
('Pedro Cutrim', 'veterano', ''),
('Gabriel Mendes', 'veterano', '')
ON CONFLICT (nome) DO NOTHING;

-- Mirins (Crianças)
INSERT INTO pessoas (nome, grupo, funcoes) VALUES
('João Gabriel', 'mirins', ''),
('Luiza', 'mirins', ''),
('Miguel', 'mirins', ''),
('Rafael', 'mirins', ''),
('Antony', 'mirins', ''),
('Maria Celida', 'mirins', ''),
('Cauan', 'mirins', ''),
('Theo', 'mirins', ''),
('Alexia', 'mirins', ''),
('Davi Barbalho', 'mirins', ''),
('Helisa', 'mirins', ''),
('Thiago Alex', 'mirins', ''),
('Gabriel Carvalho', 'mirins', ''),
('Mariana Jansen', 'mirins', ''),
('Bernardo', 'mirins', '')
ON CONFLICT (nome) DO NOTHING;

-- ============================================
-- 3. INSERIR TEMPLATES DE ESCALA
-- ============================================
-- Os templates podem ser editados a qualquer momento pela interface web
-- ou atualizando diretamente nesta tabela

-- Template Domingo Noite (18:00)
INSERT INTO escala_templates (tipo_escala, cerimoniarios_template, veteranos_template, mirins_template, turibulo_template, naveta_template, tochas_template) VALUES
('Domingo Noite',
 'Adriano, Alejandro, Alexia, Ana Julia, André, Antony, Armando, Bernardo, Cauan, Davi Barbalho, Gabriel Carvalho, Gabriel Mendes, Helisa, João Gabriel, João Raffael, Karla, Lucas, Luiza, Maria Celida, Mariana Jansen, Mateus, Miguel, Pedro Cutrim, Pedro Reis, Rafael, Sofia Reis, Theo, Thiago Alex, Vitória',
 'Adriano, Alejandro, Alexia, Ana Julia, André, Antony, Armando, Bernardo, Cauan, Davi Barbalho, Gabriel Carvalho, Gabriel Mendes, Helisa, João Gabriel, João Raffael, Karla, Lucas, Luiza, Maria Celida, Mariana Jansen, Mateus, Miguel, Pedro Cutrim, Pedro Reis, Rafael, Sofia Reis, Theo, Thiago Alex, Vitória',
 'Adriano, Alejandro, Alexia, Ana Julia, André, Antony, Armando, Bernardo, Cauan, Davi Barbalho, Gabriel Carvalho, Gabriel Mendes, Helisa, João Gabriel, João Raffael, Karla, Lucas, Luiza, Maria Celida, Mariana Jansen, Mateus, Miguel, Pedro Cutrim, Pedro Reis, Rafael, Sofia Reis, Theo, Thiago Alex, Vitória',
 '', '', '')
ON CONFLICT (tipo_escala) DO UPDATE SET
    cerimoniarios_template = EXCLUDED.cerimoniarios_template,
    veteranos_template = EXCLUDED.veteranos_template,
    mirins_template = EXCLUDED.mirins_template,
    turibulo_template = EXCLUDED.turibulo_template,
    naveta_template = EXCLUDED.naveta_template,
    tochas_template = EXCLUDED.tochas_template;

-- Template Domingo Manhã (07:00)
INSERT INTO escala_templates (tipo_escala, cerimoniarios_template, veteranos_template, mirins_template, turibulo_template, naveta_template, tochas_template) VALUES
('Domingo Manhã',
 'Adriano, Alejandro, Alexia, Ana Julia, Antony, Armando, Bernardo, Cauan, Gabriel Mendes, João Pedro, João Raffael, Karla, Mariana Jansen, Mateus, Pedro Barroso, Pedro Cutrim, Pedro Reis, Theo, Thiago Alex, Vitória',
 'Adriano, Alejandro, Alexia, Ana Julia, Antony, Armando, Bernardo, Cauan, Gabriel Mendes, João Pedro, João Raffael, Karla, Mariana Jansen, Mateus, Pedro Barroso, Pedro Cutrim, Pedro Reis, Theo, Thiago Alex, Vitória',
 'Adriano, Alejandro, Alexia, Ana Julia, Antony, Armando, Bernardo, Cauan, Gabriel Mendes, João Pedro, João Raffael, Karla, Mariana Jansen, Mateus, Pedro Barroso, Pedro Cutrim, Pedro Reis, Theo, Thiago Alex, Vitória',
 '', '', '')
ON CONFLICT (tipo_escala) DO UPDATE SET
    cerimoniarios_template = EXCLUDED.cerimoniarios_template,
    veteranos_template = EXCLUDED.veteranos_template,
    mirins_template = EXCLUDED.mirins_template,
    turibulo_template = EXCLUDED.turibulo_template,
    naveta_template = EXCLUDED.naveta_template,
    tochas_template = EXCLUDED.tochas_template;

-- Template Terça
INSERT INTO escala_templates (tipo_escala, cerimoniarios_template, veteranos_template, mirins_template, turibulo_template, naveta_template, tochas_template) VALUES
('Terça',
 'Alejandro, André, Armando, Gabriel Carvalho, João Gabriel, Karla, Lucas, Luiza, Mariana Jansen, Mateus, Pedro Barroso, Pedro Reis, Sofia Reis',
 'Alejandro, André, Armando, Gabriel Carvalho, João Gabriel, Karla, Lucas, Luiza, Mariana Jansen, Mateus, Pedro Barroso, Pedro Reis, Sofia Reis',
 'Alejandro, André, Armando, Gabriel Carvalho, João Gabriel, Karla, Lucas, Luiza, Mariana Jansen, Mateus, Pedro Barroso, Pedro Reis, Sofia Reis',
 '', '', '')
ON CONFLICT (tipo_escala) DO UPDATE SET
    cerimoniarios_template = EXCLUDED.cerimoniarios_template,
    veteranos_template = EXCLUDED.veteranos_template,
    mirins_template = EXCLUDED.mirins_template,
    turibulo_template = EXCLUDED.turibulo_template,
    naveta_template = EXCLUDED.naveta_template,
    tochas_template = EXCLUDED.tochas_template;

-- Template Quinta
INSERT INTO escala_templates (tipo_escala, cerimoniarios_template, veteranos_template, mirins_template, turibulo_template, naveta_template, tochas_template) VALUES
('Quinta',
 'Alejandro, André, Armando, Gabriel Carvalho, João Gabriel, Karla, Lucas, Luiza, Mariana Jansen, Mateus, Pedro Barroso, Pedro Cutrim, Pedro Reis',
 'Alejandro, André, Armando, Gabriel Carvalho, João Gabriel, Karla, Lucas, Luiza, Mariana Jansen, Mateus, Pedro Barroso, Pedro Cutrim, Pedro Reis',
 'Alejandro, André, Armando, Gabriel Carvalho, João Gabriel, Karla, Lucas, Luiza, Mariana Jansen, Mateus, Pedro Barroso, Pedro Cutrim, Pedro Reis',
 '', '', '')
ON CONFLICT (tipo_escala) DO UPDATE SET
    cerimoniarios_template = EXCLUDED.cerimoniarios_template,
    veteranos_template = EXCLUDED.veteranos_template,
    mirins_template = EXCLUDED.mirins_template,
    turibulo_template = EXCLUDED.turibulo_template,
    naveta_template = EXCLUDED.naveta_template,
    tochas_template = EXCLUDED.tochas_template;

-- Template Demais Dias da Semana (Segunda, Quarta, Sexta, Sábado)
INSERT INTO escala_templates (tipo_escala, cerimoniarios_template, veteranos_template, mirins_template, turibulo_template, naveta_template, tochas_template) VALUES
('Demais Dias',
 'Adriano, Alejandro, André, Armando, Davi Barbalho, Gabriel Carvalho, Helisa, João Gabriel, Karla, Lucas, Luiza, Mateus, Pedro Reis',
 'Adriano, Alejandro, André, Armando, Davi Barbalho, Gabriel Carvalho, Helisa, João Gabriel, Karla, Lucas, Luiza, Mateus, Pedro Reis',
 'Adriano, Alejandro, André, Armando, Davi Barbalho, Gabriel Carvalho, Helisa, João Gabriel, Karla, Lucas, Luiza, Mateus, Pedro Reis',
 '', '', '')
ON CONFLICT (tipo_escala) DO UPDATE SET
    cerimoniarios_template = EXCLUDED.cerimoniarios_template,
    veteranos_template = EXCLUDED.veteranos_template,
    mirins_template = EXCLUDED.mirins_template,
    turibulo_template = EXCLUDED.turibulo_template,
    naveta_template = EXCLUDED.naveta_template,
    tochas_template = EXCLUDED.tochas_template;

-- ============================================
-- 4. INSERIR DIAS DE MISSA
-- ============================================
-- Os dias de missa podem ser editados a qualquer momento pela interface web
-- ou atualizando diretamente nesta tabela

-- Domingo Manhã (dia_semana = 6, domingo)
INSERT INTO dias_missa (dia_semana, tipo_escala, horario, ativo, ordem) VALUES
(6, 'Domingo Manhã', '07:00', 1, 1)
ON CONFLICT DO NOTHING;

-- Domingo Noite (dia_semana = 6, domingo)
INSERT INTO dias_missa (dia_semana, tipo_escala, horario, ativo, ordem) VALUES
(6, 'Domingo Noite', '18:00', 1, 2)
ON CONFLICT DO NOTHING;

-- Terça (dia_semana = 1)
INSERT INTO dias_missa (dia_semana, tipo_escala, horario, ativo, ordem) VALUES
(1, 'Terça', '19:00', 1, 3)
ON CONFLICT DO NOTHING;

-- Quinta (dia_semana = 3)
INSERT INTO dias_missa (dia_semana, tipo_escala, horario, ativo, ordem) VALUES
(3, 'Quinta', '19:00', 1, 4)
ON CONFLICT DO NOTHING;

-- Demais Dias da Semana (Segunda=0, Quarta=2, Sexta=4, Sábado=5)
-- Use o template "Demais Dias" para esses dias
INSERT INTO dias_missa (dia_semana, tipo_escala, horario, ativo, ordem) VALUES
(0, 'Demais Dias', '19:00', 1, 5),  -- Segunda
(2, 'Demais Dias', '19:00', 1, 6),  -- Quarta
(4, 'Demais Dias', '19:00', 1, 7),  -- Sexta
(5, 'Demais Dias', '19:00', 1, 8)   -- Sábado
ON CONFLICT DO NOTHING;

-- ============================================
-- FIM DO SCRIPT
-- ============================================

-- Verificar dados inseridos
SELECT 'Pessoas cadastradas:' as info, COUNT(*) as total FROM pessoas;
SELECT 'Templates cadastrados:' as info, COUNT(*) as total FROM escala_templates;
SELECT 'Dias de missa configurados:' as info, COUNT(*) as total FROM dias_missa;

-- Listar pessoas por grupo
SELECT grupo, COUNT(*) as total, STRING_AGG(nome, ', ' ORDER BY nome) as nomes
FROM pessoas
GROUP BY grupo
ORDER BY grupo;

