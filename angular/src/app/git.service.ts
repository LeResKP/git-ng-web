import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';

import 'rxjs/add/operator/map';


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

  getProject(id) {
    return this.getProjects()
      .map(projects =>
        projects.find(project => project.id === +id));
  }

  getLogs(projectId, branch) {
    const url = `${baseHref}api/projects/${projectId}/logs`;
    return this.http.get(url, { params: new HttpParams().set('branch', branch) });
  }
}
