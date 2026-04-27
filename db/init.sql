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

COPY public.devices (id, user_id, name, chip_id, status, last_seen) FROM stdin;
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
9637e5fb-1885-4d82-95d2-f074ae41981b	user	user@example.com	$argon2id$v=19$m=65536,t=3,p=4$fG/tPec8J0SodS7lfA8BQA$Lbjme+7HsCzdmr7TlVJtD2FYvT/LVqRUEc9Bs0OAy1k	2026-02-05 22:18:05.297336
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

