// Copyright 2015, University of Freiburg,
// Chair of Algorithms and Data Structures.
// Hannah Bast <bast@cs.uni-freiburg.de>.

import java.io.IOException;

/**
 *
 */
public class ListIntersectionMain {

  public static void main(String[] args) throws IOException {
    String listNames[] = { "film", "comedy" };
    int m = listNames.length;
    ListIntersection li = new ListIntersection();

    // Read lists.
    PostingList lists[] = new PostingList[m];
    System.out.println();

    for (int i = 0; i < m; i++) {
      System.out.print("Reading list \"" + listNames[i] + "\" ... ");
      System.out.flush();
      String fileName = "postinglists/" + listNames[i] + ".txt";
      lists[i] = li.readPostingList(fileName, 100, 200 * 1000);
      System.out.println("done, size = " +  lists[i].ids.length);
    }
    System.out.println();

    // Performance test.
    // for (int i = 0; i < m; i++) {
    // li.performanceTest(lists[i], listNames[i]); }

    // Performance test for our intersect.
    for (int run = 0; run < 3; run++) {
      System.out.print("Intersecting \"film\" with \"comedy\" ...");
      System.out.flush();
      long time1 = System.currentTimeMillis();
      li.intersect(lists[0], lists[1]);
      long time2 = System.currentTimeMillis();
      System.out.println("done in " + (time2 - time1) + "ms");
    }
    System.out.println();
  }
}
