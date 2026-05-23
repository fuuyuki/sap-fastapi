--
-- PostgreSQL database dump
--

\restrict 7bIvZ4FQF7n0bjPs9RFfKiEXax9p9bQbncARROCzlZSDPLnpkjXKNFf4vHrwITk

-- Dumped from database version 14.23 (Ubuntu 14.23-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.23 (Ubuntu 14.23-0ubuntu0.22.04.1)

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
-- Name: device_tokens; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.device_tokens (
    id integer NOT NULL,
    user_id uuid,
    token text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.device_tokens OWNER TO fauxpg;

--
-- Name: device_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: fauxpg
--

CREATE SEQUENCE public.device_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.device_tokens_id_seq OWNER TO fauxpg;

--
-- Name: device_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fauxpg
--

ALTER SEQUENCE public.device_tokens_id_seq OWNED BY public.device_tokens.id;


--
-- Name: devices; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.devices (
    chip_id character varying(100) NOT NULL,
    name character varying(100) NOT NULL,
    status character varying(50) DEFAULT 'offline'::character varying,
    last_seen timestamp with time zone DEFAULT now() NOT NULL,
    api_key character varying(255) NOT NULL,
    patient_id uuid NOT NULL
);


ALTER TABLE public.devices OWNER TO fauxpg;

--
-- Name: medlogs; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.medlogs (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    patient_id uuid NOT NULL,
    device_id character varying(100) NOT NULL,
    pillname character varying(100) NOT NULL,
    scheduled_time timestamp without time zone DEFAULT now() NOT NULL,
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
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.notifications OWNER TO fauxpg;

--
-- Name: schedules; Type: TABLE; Schema: public; Owner: fauxpg
--

CREATE TABLE public.schedules (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    patient_id uuid NOT NULL,
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
    password character varying(255) NOT NULL,
    role character varying(50) NOT NULL,
    caretaker_id uuid,
    CONSTRAINT patient_caretaker_check CHECK (((((role)::text = 'patient'::text) AND (caretaker_id IS NOT NULL)) OR (((role)::text = 'caretaker'::text) AND (caretaker_id IS NULL)))),
    CONSTRAINT role_check CHECK (((role)::text = ANY ((ARRAY['caretaker'::character varying, 'patient'::character varying])::text[])))
);


ALTER TABLE public.users OWNER TO fauxpg;

--
-- Name: device_tokens id; Type: DEFAULT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.device_tokens ALTER COLUMN id SET DEFAULT nextval('public.device_tokens_id_seq'::regclass);


--
-- Data for Name: device_tokens; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.device_tokens (id, user_id, token, created_at) FROM stdin;
\.


--
-- Data for Name: devices; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.devices (chip_id, name, status, last_seen, api_key, patient_id) FROM stdin;
00DE3855B594	SAP04	offline	2026-04-29 20:56:45.215071+07	71d3880b72db1e18f23cec342897fb155b25de1876990f08e6e1c173a53ef754	d7bec72c-9f55-4822-a44d-c931560ac24b
F0B5AD286F24	SAP03	offline	2026-04-29 01:06:44.509549+07	08f5d1f653b0b65ef3b4600e74890fcc06b1130733023142e0658ee9a338bb8c	f424f3f6-e4b2-40c9-bf40-89dc4fa70a68
C87BC4286F24	SAP02	offline	2026-04-29 01:05:45.517765+07	b6d1c1cda37e9e8bd4d3730d8a20f51882c5f97075b2cdc18c683f320a3172bb	c6f61142-69bf-422b-90d3-55840e9e8957
F4A2B6B24354	SAP01	offline	2026-04-29 00:47:31.678455+07	7cc30933c7b4ad980886fda2e58f1e01539d30620449bd05e742c6c1d2fffd04	a82cb96f-bd51-4a2a-913f-8cf15fcea40a
\.


--
-- Data for Name: medlogs; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.medlogs (id, patient_id, device_id, pillname, scheduled_time, status) FROM stdin;
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.notifications (id, device_id, user_id, message, created_at) FROM stdin;
\.


--
-- Data for Name: schedules; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.schedules (id, patient_id, device_id, pillname, dose_time, repeat_days) FROM stdin;
efdafa04-5233-43e8-9ea8-4f61b943a073	a82cb96f-bd51-4a2a-913f-8cf15fcea40a	F4A2B6B24354	Obat1	00:07:12.281	127
c9031fe9-0fed-46d9-a6c8-9a93df92be90	c6f61142-69bf-422b-90d3-55840e9e8957	C87BC4286F24	Obat2	00:07:12.281	127
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: fauxpg
--

COPY public.users (id, name, email, password, role, caretaker_id) FROM stdin;
a82cb96f-bd51-4a2a-913f-8cf15fcea40a	Patient1	patient1@gmail.com	$argon2id$v=19$m=65536,t=3,p=4$AiAEYKw1xhijdE5JaS3FeA$JkLeqJNjhqb3TTbLOINvgTTKbSPJTuD4FjpLgwxrWlU	patient	b179642d-8a6c-40ae-a1e7-775e16a752c0
c6f61142-69bf-422b-90d3-55840e9e8957	Patient2	patient2@gmail.com	$argon2id$v=19$m=65536,t=3,p=4$8d47x/jfm3NOqdVa6x2D0A$6+0rbEJy7tf6XLTazfgzGydtov/CL5MLoaTNH+lYuzc	patient	b179642d-8a6c-40ae-a1e7-775e16a752c0
f424f3f6-e4b2-40c9-bf40-89dc4fa70a68	Patient3	patient3@gmail.com	$argon2id$v=19$m=65536,t=3,p=4$3PsfQ8hZy3lv7T0nBCDEeA$I0MdyhWYvuusK3SwpyPRAWnF16iGE+wmhMhA0MhA8LU	patient	b179642d-8a6c-40ae-a1e7-775e16a752c0
d7bec72c-9f55-4822-a44d-c931560ac24b	Patient4	patient4@gmail.com	$argon2id$v=19$m=65536,t=3,p=4$RWiNUYqxFgLA+L+X8j4nRA$00t8g4YXWZQfuxChvvNFBu1CYE39EQd6Ujh6sFh80mg	patient	b179642d-8a6c-40ae-a1e7-775e16a752c0
b179642d-8a6c-40ae-a1e7-775e16a752c0	Caretaker	caretaker@gmail.com	$argon2id$v=19$m=65536,t=3,p=4$7L1XyjnHeM/Zm/M+J4TwPg$qe71LEgKzTFASqW58KwF/CCfja/o3tNcQmEP+I65rvc	caretaker	\N
\.


--
-- Name: device_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: fauxpg
--

SELECT pg_catalog.setval('public.device_tokens_id_seq', 1, false);


--
-- Name: device_tokens device_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.device_tokens
    ADD CONSTRAINT device_tokens_pkey PRIMARY KEY (id);


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
-- Name: device_tokens device_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.device_tokens
    ADD CONSTRAINT device_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: devices devices_patient_fk; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_patient_fk FOREIGN KEY (patient_id) REFERENCES public.users(id);


--
-- Name: medlogs medlogs_device_fk; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.medlogs
    ADD CONSTRAINT medlogs_device_fk FOREIGN KEY (device_id) REFERENCES public.devices(chip_id);


--
-- Name: medlogs medlogs_patient_fk; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.medlogs
    ADD CONSTRAINT medlogs_patient_fk FOREIGN KEY (patient_id) REFERENCES public.users(id);


--
-- Name: schedules schedules_device_fk; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_device_fk FOREIGN KEY (device_id) REFERENCES public.devices(chip_id);


--
-- Name: schedules schedules_patient_fk; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_patient_fk FOREIGN KEY (patient_id) REFERENCES public.users(id);


--
-- Name: users users_caretaker_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fauxpg
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_caretaker_id_fkey FOREIGN KEY (caretaker_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict 7bIvZ4FQF7n0bjPs9RFfKiEXax9p9bQbncARROCzlZSDPLnpkjXKNFf4vHrwITk

