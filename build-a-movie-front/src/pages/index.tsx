import Head from "next/head";
import Image from "next/image";
import { Footer } from "../components/Footer";
import Select from "react-select";
import { useQuery } from "react-query";
import { useState } from "react";
import {
  useActors,
  useBoxOfficePrediction,
  useDirectors,
  useGenres,
  useRatingPrediction,
} from "../hooks/queries";

type ResultActors = {
  actors: {
    name: string;
  }[];
};

type ResultDirectors = {
  directors: {
    name: string;
  }[];
};

type Query = [string, { query: string }];

type SelectFunction = Array<{ value: string; label: string }>;

export default function Home() {
  const [actorQuery, setActorQuery] = useState("");
  const [directorQuery, setDirectorQuery] = useState("");
  const [budget, setBudget] = useState(1000000);

  const [directors, setDirectors] = useState<Array<string>>([
    "Stanley Kubrick",
  ]);
  const [actors, setActors] = useState<Array<string>>(["Tom Cruise"]);
  const [genres, setGenres] = useState<Array<string>>(["Horror"]);

  const { data: genreOptions, isLoading } = useGenres();
  const { data: actorOptions, isLoading: isLoadingActors } =
    useActors(actorQuery);
  const { data: directorOptions, isLoading: isLoadingDirectors } =
    useDirectors(directorQuery);

  const {
    data: boxOffice,
    refetch: getBoxOffice,
    isLoading: loadingBoxOffice,
  } = useBoxOfficePrediction({
    budget,
    directors,
    actors,
    genres,
  });

  const {
    data: rating,
    refetch: getRating,
    isLoading: loadingRating,
  } = useRatingPrediction({
    budget,
    directors,
    actors,
    genres,
  });

  const getResult = () => {
    getBoxOffice();
    getRating();
  };

  console.log(loadingBoxOffice, loadingRating, rating, boxOffice);

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
              and budget.
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
              defaultValue={[
                { label: "Stanley Kubrick", value: "Stanley Kubrick" },
              ]}
              onInputChange={(value) => setDirectorQuery(value)}
              onChange={(value) => setDirectors(value.map((v) => v.value))}
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
              defaultValue={[{ label: "Tom Cruise", value: "Tom Cruise" }]}
              onChange={(value) => setActors(value.map((v) => v.value))}
              onInputChange={(value) => setActorQuery(value)}
              isLoading={isLoadingActors}
              options={actorOptions}
            />
          </div>

          <div className="py-10">
            <div className="mb-5">
              <label className="font-bold text-white">Select genre(s)</label>
            </div>
            <Select
              defaultValue={[{ label: "Horror", value: "Horror" }]}
              onChange={(value) => setGenres(value.map((v) => v.value))}
              isMulti
              options={genreOptions}
              isLoading={isLoading}
            />
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

          <div className="py-10 shadow">
            <h3>{boxOffice}</h3>
            <h3>{rating}</h3>
          </div>
        </div>
      </main>
    </div>
  );
}
