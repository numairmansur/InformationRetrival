// Copyright 2015, University of Freiburg,
// Chair of Algorithms and Data Structures.
// Hannah Bast <bast@cs.uni-freiburg.de>.

import java.util.ArrayList;
import java.io.FileReader;
import java.io.BufferedReader;
import java.io.IOException;

/**
 * Code for intersecting two posting lists.
 */
public class ListIntersection {

  /**
   * Read posting list from file.
   */
  PostingList readPostingList(String fileName,
      int numRepeats, int offset) throws IOException {
    FileReader fileReader = new FileReader(fileName);
    BufferedReader bufferedReader = new BufferedReader(fileReader);
    ArrayList<Integer> ids = new ArrayList<Integer>();
    ArrayList<Integer> scores = new ArrayList<Integer>();

    while (true) {
      String line = bufferedReader.readLine();
      if (line == null) { break; }
      String[] parts = line.split("\\W+");
      ids.add(Integer.parseInt(parts[0]));
      scores.add(Integer.parseInt(parts[1]));
    }

    return new PostingList(ids, scores, numRepeats, offset);
  }

  /**
   * Simple performance test: compute the sum over all ids of a posting list.
   */
  void performanceTest(PostingList list, String name) {
    // for (int run = 0; run < 3; run++) {
    //   System.out.print("Computing checksum for \"" + name
    //       + "\" with ArrayList ... ");
    //   System.out.flush();
    //   long time1 = System.currentTimeMillis();
    //   int sum = 0;
    //   for (int i = 0; i < list.ids.size(); i++) { sum += list.ids.get(i); }
    //   long time2 = System.currentTimeMillis();
    //   System.out.println("done in " + (time2 - time1) + "ms");
    // }
    // System.out.println();

    int n = list.ids.length;
    int ids[] = new int[n];
    int scores[] = new int[n];

    for (int i = 0; i < n; i++) {
      ids[i] = list.ids[i];
      scores[i] = list.scores[i];
    }

    for (int run = 0; run < 3; run++) {
      System.out.print("Computing checksum for \"" + name
          + "\" with native arrays ... ");
      System.out.flush();
      long time1 = System.currentTimeMillis();
      int sum = 0;
      for (int i = 0; i < n; i++) { sum += ids[i]; }
      long time2 = System.currentTimeMillis();
      System.out.println("done in " + (time2 - time1) + "ms");
    }
    System.out.println();
  }

  /**
   * Simple linear-time intersect.
   */
  PostingList intersect(PostingList list1, PostingList list2) {
    int n1 = list1.ids.length;
    int n2 = list2.ids.length;
    int i = 0;
    int j = 0;
    ArrayList<Integer> ids = new ArrayList<Integer>();
    ArrayList<Integer> scores = new ArrayList<Integer>();

    while (i < n1 && j < n2) {
      while (i < n1 && list1.ids[i] < list2.ids[j]) { i++; }
      if (i == n1) { break; }
      while (j < n2 && list2.ids[j] < list1.ids[i]) { j++; }
      if (j == n2) { break; }
      if (list1.ids[i] == list2.ids[j]) {
        ids.add(list1.ids[i]);
        scores.add(list1.scores[i] + list2.scores[j]);
        i++;
        j++;
      }
    }
    // while (i < n1 && j < n2) {
    //   if (list1.ids[i] < list2.ids[j]) { i++; }
    //   if (i == n1) { break; }
    //   if (list2.ids[j] < list1.ids[i]) { j++; }
    //   if (j == n2) { break; }
    //   if (list1.ids[i] == list2.ids[j]) {
    //     ids.add(list1.ids[i]);
    //     scores.add(list1.scores[i] + list2.scores[j]);
    //     i++;
    //     j++;
    //   }
    // }

    return new PostingList(ids, scores, 1, 0);
  }
}
