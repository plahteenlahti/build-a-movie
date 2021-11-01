// Next.js API route support: https://nextjs.org/docs/api-routes/introduction

export default async function handler(req, res) {
  async function fetchGraphQL(query: string) {
    return fetch(`https://meet-spider-88.hasura.app/v1/graphql`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-hasura-admin-secret": `${process.env.HASURA_TOKEN}`,
      },
      body: JSON.stringify({ query }),
    }).then((response) => response.json());
  }

  const query = await req.body;
  const result = await fetchGraphQL(`query {
    actors(limit: 100, where: {name: {_ilike: "%${query.query ?? ""}%"}}) {
      name
    }
  }`);
  res.status(200).json({ ...result?.data });
}
