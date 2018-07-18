import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';

import { Observable, ReplaySubject, Subscription } from 'rxjs/Rx';
import 'rxjs/add/operator/map';

import { shareReplay, map } from 'rxjs/operators';

import { BehaviorSubject } from 'rxjs/BehaviorSubject';


const baseHref = 'http://127.0.0.1:6543/';

const API_URLS: any = {
  projects: `${baseHref}api/projects`,
};


@Injectable()
export class GitService {

  commitHash: ReplaySubject<string> = new ReplaySubject(1);

  private _projects$: Observable<Array<any>>;

  constructor(private http: HttpClient) { }


  setCommitHash(hash) {
    this.commitHash.next(hash);
  }

  get projects$() {
    if (!this._projects$) {
      this._projects$ = this.http.get<[any]>(API_URLS.projects).pipe(shareReplay(1));
    }
    return this._projects$;
  }

  getProject(id) {
    return this.projects$
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
