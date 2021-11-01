import Head from "next/head";
import Image from "next/image";
import { Footer } from "../components/Footer";
import Select from "react-select";
import { useQuery } from "react-query";
import { useState } from "react";

type Result = {
  data: {
    actors: {
      name: string;
    }[];
  };
};

type Query = [string, { query: string }];

type Select = Array<{ value: string; label: string }>;

export default function Home() {
  const [actorQuery, setActorQuery] = useState("Leonardo");

  const { data: genreOptions, isLoading } = useQuery(
    "genres",
    async () => await (await fetch("/api/genres")).json(),
    {
      select: (data) =>
        data.genres.map((genre) => ({
          value: `${genre}`.toLowerCase(),
          label: genre,
        })),
    }
  );

  const { data: actorOptions, isLoading: isLoadingActors } = useQuery<
    Result,
    unknown,
    Select,
    Query
  >(
    ["actors", { query: actorQuery }],
    async ({ queryKey }) => {
      const [_key, { query }] = queryKey;

      const response = await fetch("/api/actors", {
        method: "POST",
        body: JSON.stringify({ query: query }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      console.log("response", data);
      return data;
    },
    {
      select: ({ data }) =>
        data.actors.map(({ name }) => ({
          value: `${name}`.toLowerCase(),
          label: name,
        })),
      enabled: false,
    }
  );

  const { data: directorOptions, isLoading: isLoadingDirectors } = useQuery<
    Result,
    unknown,
    Select,
    Query
  >(
    ["actors", { query: actorQuery }],
    async ({ queryKey }) => {
      const [_key, { query }] = queryKey;

      const response = await fetch("/api/directors", {
        method: "POST",
        body: JSON.stringify({ query: query }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      console.log("response", data);
      return data;
    },
    {
      select: ({ data }) =>
        data.actors.map(({ name }) => ({
          value: `${name}`.toLowerCase(),
          label: name,
        })),
      enabled: false,
    }
  );

  const getResult = async () => {
    try {
      const data = await fetch("http://167.172.109.147/predict-rating", {
        method: "POST",
        mode: "no-cors",
        body: JSON.stringify({
          people: ["Tom Cruise"],
          genres: ["News"],
          budget: 20000,
        }),
      });

      const score = await data?.body;

      console.log("response", score);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div>
      <Head>
        <title>Build-A-Movie</title>
        <meta
          name="description"
          content=" Create the perfect movie by selecting the right actors, directors
              etc..."
        />
        <link
          rel="stylesheet"
          href="https://use.fontawesome.com/releases/v5.11.2/css/all.css"
        />

        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gray-800">
        <div className="relative bg-red-800">
          <div className="absolute inset-0">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              className="object-cover w-full h-full"
              src="https://images.unsplash.com/photo-1440404653325-ab127d49abc1?ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&ixlib=rb-1.2.1&auto=format&fit=crop&w=2970&q=800"
              alt=""
            />
            <div
              className="absolute inset-0 bg-red-800 mix-blend-multiply"
              aria-hidden="true"
            />
          </div>
          <div className="relative px-4 py-24 mx-auto max-w-7xl sm:py-32 sm:px-6 lg:px-8">
            <h1 className="text-4xl font-extrabold tracking-tight text-center text-white sm:text-5xl lg:text-6xl">
              Build-A-Movie
            </h1>
            <p className="max-w-3xl mx-auto mt-6 text-xl text-center text-red-100">
              Create the perfect movie by selecting the right actors, directors
              etc...
            </p>
          </div>
        </div>
        <nav className="max-w-screen-lg px-3 py-6 mx-auto"></nav>

        <div className="max-w-screen-lg px-3 pt-20 pb-32 mx-auto">
          <div className="py-10">
            <div className="mb-5">
              <label className="font-bold text-white">Select director(s)</label>
            </div>
            <Select
              isMulti
              options={directorOptions}
              isLoading={isLoadingDirectors}
            />
          </div>

          <div className="py-10">
            <div className="mb-5">
              <label className="font-bold text-white">Select actor(s)</label>
            </div>
            <Select
              isMulti
              onInputChange={(value) => setActorQuery(value)}
              isLoading={isLoadingActors}
              options={actorOptions}
            />

            <div className="py-10">
              <div className="mb-5">
                <label className="font-bold text-white">Select genre(s)</label>
              </div>
              <Select isMulti options={genreOptions} isLoading={isLoading} />
            </div>
          </div>

          <div className="flex justify-center py-10">
            <button
              type="button"
              onClick={getResult}
              className="inline-flex items-center px-6 py-3 text-base font-medium text-white bg-red-600 border border-transparent rounded-md shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              Estimate score
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
