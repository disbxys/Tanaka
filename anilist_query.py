import json
import requests


url = "https://graphql.anilist.co"

def query_id(id):
    query = '''
query ($id: Int) {
  Media (id: $id, type: ANIME) {
    id
    idMal
    title {
      romaji
      english
      native
    }
    season
    seasonYear
    tags {
      id
      name
      rank
    }
  }
}
'''
    variables = { "id": id }
    return requests.post(url, json={"query": query, "variables": variables}).json()

def query_idMal(idMal):
    query = '''
query ($idMal: Int) {
  Media(idMal: $idMal, type: ANIME) {
    id
    idMal
    episodes
    title {
      romaji
      english
      native
      userPreferred
    }
    synonyms
    status
    season
    seasonYear
    genres
    tags {
      name
    }
    source
    duration
    studios {
      edges {
        node {
          name
        }
      }
    }
    averageScore
    popularity
  }
}
'''
    variables = { "idMal": idMal }
    return requests.post(url, json={"query": query, "variables": variables}).json()


def query_username(username):
    query = '''
query ($username: String) {
  MediaListCollection(userName: $username, type: ANIME) {
    user {
        id
        name
    }
    lists {
      name
      entries {
        id
        status
        progress
        media {
          chapters
          volumes
          idMal
          episodes
          title {
            english
            romaji
            native
          }
        }
        score(format: POINT_10)
        notes
        repeat
      }
      name
      isCustomList
      isSplitCompletedList
      status
    }
  }
}
'''
    variables = { "username": username }
    return requests.post(url, json={"query": query, "variables": variables}).json()


def query_search(keyword, page=1, per_page=5):
    query = '''
query ($id: Int, $page: Int, $perPage: Int, $search: String) {
    Page (page: $page, perPage: $perPage) {
        pageInfo {
            total
            currentPage
            lastPage
            hasNextPage
            perPage
        }
        media (id: $id, search: $search, type: ANIME) {
            id
            title {
                romaji
                english
                native
            }
            season
            seasonYear
        }
    }
}
'''
    variables = {
        "search": keyword,
        "page": page,
        "perPage": per_page
    }
    return requests.post(url, json={"query": query, "variables": variables}).json()