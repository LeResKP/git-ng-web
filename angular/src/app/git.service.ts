import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';


const baseHref = 'http://127.0.0.1:6543/';

const API_URLS: any = {
  projects: `${baseHref}api/projects`,
};


@Injectable()
export class GitService {

  constructor(private http: HttpClient) { }

  getProjects() {
    return this.http.get(API_URLS.projects);
  }
}
