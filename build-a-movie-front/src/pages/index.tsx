import Head from "next/head";
import Image from "next/image";
import { Footer } from "../components/Footer";
import Select from "react-select";
import { useQuery } from "react-query";
import { useState } from "react";

export default function Home() {
  const [actorQuery, setActorQuery] = useState("Leonardo");

  const options = [
    { value: "chocolate", label: "Chocolate" },
    { value: "strawberry", label: "Strawberry" },
    { value: "vanilla", label: "Vanilla" },
  ];

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

  const { data: actorOptions, isLoading: isLoadingActors } = useQuery(
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
    }
  );

  console.log(actorOptions, isLoadingActors);

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

      <main className="bg-gray-100">
        <nav className="max-w-screen-lg mx-auto px-3 py-6"></nav>

        <div className="max-w-screen-lg mx-auto px-3 pt-20 pb-32">
          <header className="text-center">
            <h1 className="text-5xl text-gray-900 font-bold whitespace-pre-line leading-hero">
              Build-A-<span className="text-primary-500">Movie</span>
            </h1>
            <div className="text-2xl mt-4 mb-16">
              Create the perfect movie by selecting the right actors, directors
              etc...
            </div>
          </header>

          <div className="py-10">
            <div className="mb-5">
              <label className="font-bold">Select director(s)</label>
            </div>
            <Select isMulti options={options} isLoading={isLoading} />
          </div>

          <div className="py-10">
            <div className="mb-5">
              <label className="font-bold">Select actor(s)</label>
            </div>
            <Select
              isMulti
              onInputChange={(value) => setActorQuery(value)}
              isLoading={isLoadingActors}
              options={actorOptions}
            />
          </div>

          <div className="py-10">
            <div className="mb-5">
              <label className="font-bold">Select genre(s)</label>
            </div>
            <Select isMulti options={genreOptions} isLoading={isLoading} />
          </div>
        </div>

        <Footer />
      </main>
    </div>
  );
}
