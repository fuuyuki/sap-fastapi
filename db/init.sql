--
-- PostgreSQL database dump
--

\restrict gCDgzdhk65mm4z4LcztKhiV9e0hUE222s0UPsZBTBJPlyScGXKUkXdJFRGNlkbt

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


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: devices; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.devices (
    chip_id character varying(100) NOT NULL,
    user_id uuid NOT NULL,
    name character varying(100) NOT NULL,
    status character varying(50) DEFAULT 'offline'::character varying,
    last_seen timestamp with time zone DEFAULT now() NOT NULL,
    api_key character varying(255) NOT NULL
);


ALTER TABLE public.devices OWNER TO fauxpg;

--
-- Name: medlogs; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.medlogs (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    device_id character varying(100) NOT NULL,
    pillname character varying(100) NOT NULL,
    scheduled_time timestamp without time zone NOT NULL,
    status character varying(50) NOT NULL
);


ALTER TABLE public.medlogs OWNER TO fauxpg;

--
-- Name: notifications; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.notifications (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    device_id character varying(100) NOT NULL,
    user_id uuid NOT NULL,
    message character varying(255) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.notifications OWNER TO fauxpg;

--
-- Name: schedules; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.schedules (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    device_id character varying(100) NOT NULL,
    pillname character varying(100) NOT NULL,
    dose_time time without time zone NOT NULL,
    repeat_days integer DEFAULT 0
);


ALTER TABLE public.schedules OWNER TO fauxpg;

--
-- Name: users; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.users (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(50) DEFAULT 'patient'::character varying NOT NULL
);


ALTER TABLE public.users OWNER TO fauxpg;

--
-- Data for Name: devices; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.devices (chip_id, user_id, name, status, last_seen, api_key) FROM stdin;
C87BC4286F24    fd1ff641-ec8a-4424-9c1f-4b5c1f2c91e6    SAP02   offline \N  7bc8fb1d87efb2b54de66525db07b215eeb71a11a034f1cb7215cda6058caa4d
\.


--
-- Data for Name: medlogs; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.medlogs (id, user_id, device_id, pillname, scheduled_time, status) FROM stdin;
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.notifications (id, device_id, user_id, message, created_at) FROM stdin;
\.


--
-- Data for Name: schedules; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.schedules (id, user_id, device_id, pillname, dose_time, repeat_days) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.users (id, name, email, password_hash, role) FROM stdin;
fd1ff641-ec8a-4424-9c1f-4b5c1f2c91e6	string	user@example.com	$argon2id$v=19$m=65536,t=3,p=4$7L1XyjnHeM/Zm/M+J4TwPg$qe71LEgKzTFASqW58KwF/CCfja/o3tNcQmEP+I65rvc	patient
\.


--
-- Name: devices devices_pkey; Type: CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_pkey PRIMARY KEY (chip_id);


--
-- Name: medlogs medlogs_pkey; Type: CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.medlogs
    ADD CONSTRAINT medlogs_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


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
-- Name: devices devices_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: medlogs medlogs_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.medlogs
    ADD CONSTRAINT medlogs_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(chip_id);


--
-- Name: medlogs medlogs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.medlogs
    ADD CONSTRAINT medlogs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: notifications notifications_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(chip_id);


--
-- Name: notifications notifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: schedules schedules_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(chip_id);


--
-- Name: schedules schedules_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict gCDgzdhk65mm4z4LcztKhiV9e0hUE222s0UPsZBTBJPlyScGXKUkXdJFRGNlkbt

