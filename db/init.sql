--
-- PostgreSQL database dump
--

\restrict cMfsPrsxaEeMeVLIMAbbbiFTuldsKFUd3Q2bfrcR6AyctlDqs3FzuXHjM0AL6PU

-- Dumped from database version 14.20 (Ubuntu 14.20-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.20 (Ubuntu 14.20-0ubuntu0.22.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: command_enum; Type: TYPE; Schema: public; Owner: fauxpg
--

CREATE TYPE public.command_enum AS ENUM (
    'reset',
    'snooze'
);


ALTER TYPE public.command_enum OWNER TO fauxpg;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO fauxpg;

--
-- Name: commands; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.commands (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    device_id uuid NOT NULL,
    command public.command_enum NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.commands OWNER TO fauxpg;

--
-- Name: devices; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.devices (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    name character varying(100) NOT NULL,
    chip_id character varying(100) NOT NULL,
    status text DEFAULT 'offline'::text,
    last_seen timestamp with time zone
);


ALTER TABLE public.devices OWNER TO fauxpg;

--
-- Name: medlogs; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.medlogs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    device_id uuid NOT NULL,
    pillname character varying(100),
    taken_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    status character varying(20),
    schedule_time timestamp without time zone,
    CONSTRAINT medlogs_status_check CHECK (((status)::text = ANY ((ARRAY['taken'::character varying, 'missed'::character varying])::text[])))
);


ALTER TABLE public.medlogs OWNER TO fauxpg;

--
-- Name: schedules; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.schedules (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    device_id uuid NOT NULL,
    pillname character varying(100) NOT NULL,
    repeat_days integer DEFAULT 0,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    dose_time time without time zone NOT NULL
);


ALTER TABLE public.schedules OWNER TO fauxpg;

--
-- Name: users; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.users (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(150) NOT NULL,
    password text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO fauxpg;

--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.alembic_version (version_num) FROM stdin;
add_uuid_default
111aaa
222bbb
7d808d5319fa
\.


--
-- Data for Name: commands; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.commands (id, user_id, device_id, command, created_at) FROM stdin;
\.


--
-- Data for Name: devices; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.devices (id, user_id, name, chip_id, status, last_seen, api_key) FROM stdin;
00DE3855B594	fd1ff641-ec8a-4424-9c1f-4b5c1f2c91e6	SAP04	offline	2026-04-19 06:45:50.728122+07	71d3880b72db1e18f23cec342897fb155b25de1876990f08e6e1c173a53ef754
F0B5AD286F24	fd1ff641-ec8a-4424-9c1f-4b5c1f2c91e6	SAP03	offline	2026-04-19 06:45:41.367051+07	08f5d1f653b0b65ef3b4600e74890fcc06b1130733023142e0658ee9a338bb8c
F4A2B6B24354	fd1ff641-ec8a-4424-9c1f-4b5c1f2c91e6	SAP01	offline	2026-04-19 06:45:27.211085+07	7cc30933c7b4ad980886fda2e58f1e01539d30620449bd05e742c6c1d2fffd04
C87BC4286F24	fd1ff641-ec8a-4424-9c1f-4b5c1f2c91e6	SAP02	offline	2026-02-12 23:00:32.743838+07	b6d1c1cda37e9e8bd4d3730d8a20f51882c5f97075b2cdc18c683f320a3172bb
\.


--
-- Data for Name: medlogs; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.medlogs (id, user_id, device_id, pillname, taken_at, status, schedule_time) FROM stdin;
\.


--
-- Data for Name: schedules; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.schedules (id, user_id, device_id, pillname, repeat_days, created_at, dose_time) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.users (id, name, email, password, created_at) FROM stdin;
fd1ff641-ec8a-4424-9c1f-4b5c1f2c91e6	Caretaker	caretaker@gmail.com	$argon2id$v=19$m=65536,t=3,p=4$7L1XyjnHeM/Zm/M+J4TwPg$qe71LEgKzTFASqW58KwF/CCfja/o3tNcQmEP+I65rvc	caretaker
a87b9694-fdc7-44be-97fd-ce46ec172736	Patient	patient@gmail.com	$argon2id$v=19$m=65536,t=3,p=4$B6A0ZgzBeO/d+19LCYEQwg$AzcpYGrH4LQr4BAnFoCzs5afkNrtIWpZY3NCwDBSxYA	patient
a0f717b8-17c2-480c-b181-c86ef83a0419	Admin	admin@gmail.com	$argon2id$v=19$m=65536,t=3,p=4$6r3XGkNobc0ZozRmrDWmlA$ESU9mO9rxRLLhJRzsNxW0k9iqXZIuDrW7wYY21fSqLA	caretaker
\.


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: commands commands_pkey; Type: CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.commands
    ADD CONSTRAINT commands_pkey PRIMARY KEY (id);


--
-- Name: devices devices_chip_id_key; Type: CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_chip_id_key UNIQUE (chip_id);


--
-- Name: devices devices_pkey; Type: CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_pkey PRIMARY KEY (id);


--
-- Name: medlogs medlogs_pkey; Type: CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.medlogs
    ADD CONSTRAINT medlogs_pkey PRIMARY KEY (id);


--
-- Name: schedules schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: commands commands_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.commands
    ADD CONSTRAINT commands_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id) ON DELETE CASCADE;


--
-- Name: commands commands_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.commands
    ADD CONSTRAINT commands_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: devices devices_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: medlogs medlogs_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.medlogs
    ADD CONSTRAINT medlogs_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id) ON DELETE CASCADE;


--
-- Name: medlogs medlogs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.medlogs
    ADD CONSTRAINT medlogs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: schedules schedules_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id) ON DELETE CASCADE;


--
-- Name: schedules schedules_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict cMfsPrsxaEeMeVLIMAbbbiFTuldsKFUd3Q2bfrcR6AyctlDqs3FzuXHjM0AL6PU

