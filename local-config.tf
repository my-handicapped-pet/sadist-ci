# describe how to build an image
# image name -> {"repo": [repo1, repo2], "dockerfile": "repo1/Dokcerfile"}...
locals {
  config = {
    webapp-flask = {
      repo       = ["my-handicapped-pet/sadist-be", "my-handicapped-pet/sadist-fe"]
      dockerfile = "./sadist-be/Dockerfile-flask"
    }
    task-queue = {
      repo       = ["my-handicapped-pet/sadist-be"]
      dockerfile = "./sadist-be/Dockerfile-task-queue"
    }
    webapp-nginx = {
      repo       = ["my-handicapped-pet/sadist-be"]
      dockerfile = "./sadist-be/Dockerfile-nginx"
    }
    certbot = {
      repo       = ["my-handicapped-pet/sadist-be"]
      dockerfile = "./sadist-be/Dockerfile-certbot"
    }
    webapp-proxy = {
      repo       = ["my-handicapped-pet/sadist-proxy"]
      dockerfile = "./sadist-proxy/Dockerfile-proxy"
    }
    webapp-map = {
      repo       = ["my-handicapped-pet/sadist-map"]
      dockerfile = "./sadist-map/Dockerfile-map"
    }
    blog-app = {
      repo       = ["my-handicapped-pet/sadist-blog"]
      dockerfile = "./sadist-blog/Dockerfile-blog"
    }
    blog-admin-app = {
      repo       = ["my-handicapped-pet/sadist-blog"]
      dockerfile = "./sadist-blog/Dockerfile-blog-admin"
    }
    job-scraper = {
      repo       = ["my-handicapped-pet/job-scraper"]
      dockerfile = "./job-scraper/Dockerfile"
    }
  }
}
