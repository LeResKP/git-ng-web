import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';

import { Observable, ReplaySubject } from 'rxjs/Rx';
import 'rxjs/add/operator/map';


const baseHref = 'http://127.0.0.1:6543/';

const API_URLS: any = {
  projects: `${baseHref}api/projects`,
};


@Injectable()
export class GitService {

  commitHash: ReplaySubject<string> = new ReplaySubject(1);

  constructor(private http: HttpClient) { }


  setCommitHash(hash) {
    this.commitHash.next(hash);
  }

  getProjects(): Observable<[any]> {
    return this.http.get<[any]>(API_URLS.projects);
  }

  getProject(id) {
    return this.getProjects()
      .map(projects =>
        projects.find(project => project.id === +id));
  }

  getLogs(projectId, branch, rev, skip) {
    const url = `${baseHref}api/projects/${projectId}/logs`;
    let params = new HttpParams();
    params = params.append('branch', branch);
    if (rev) { params = params.append('rev', rev); }
    if (skip) { params = params.append('skip', skip); }
    return this.http.get(url, { params });
  }

  getLogDetails(projectId, hash) {
    const url = `${baseHref}api/projects/${projectId}/logs/${hash}`;
    return this.http.get(url);
  }

  getDiff(projectId, hash) {
    const url = `${baseHref}api/projects/${projectId}/diff/${hash}`;
    return this.http.get(url);
  }

  getContextDiff(projectId, hash, path, data) {
    const url = `${baseHref}api/projects/${projectId}/diff/${hash}/context`;
    return this.http.post(url, { path, data });
  }

  tree(projectId, hash, path) {
    let params = new HttpParams();
    // NOTE: path can be null
    params = params.append('path', path || '');
    const url = `${baseHref}api/projects/${projectId}/tree/${hash}`;
    return this.http.get(url, {params});
  }

  blob(projectId, hash, path) {
    let params = new HttpParams();
    // NOTE: path can be null
    params = params.append('path', path || '');
    const url = `${baseHref}api/projects/${projectId}/blob/${hash}`;
    return this.http.get(url, {params});
  }
}
